from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.conf import settings
import json
import requests
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def telegram_webhook(request):
    """
    Handle incoming Telegram updates (Webhook).
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'ok'})
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'status': 'error'}, status=400)
    
    # Handle Callback Query (Button Clicks)
    if 'callback_query' in data:
        process_callback(data['callback_query'])
    
    return JsonResponse({'status': 'ok'})

def process_callback(callback):
    """
    Process button clicks (Approve/Deny).
    """
    callback_id = callback.get('id')
    data = callback.get('data')
    message = callback.get('message')
    
    if not data or '_' not in data:
        return

    action, user_id = data.split('_')
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    
    response_text = ""
    
    try:
        user = User.objects.get(id=user_id)
        
        if action == 'approve':
            user.is_active = True
            user.save()
            response_text = f"✅ User *{user.username}* has been APPROVED."
        elif action == 'deny':
            # Delete the user so they can try again or just to clear the record
            user.delete()
            response_text = f"❌ User *{user.username}* has been DENIED and deleted."
            
    except User.DoesNotExist:
        response_text = "⚠️ User record not found."
    except Exception as e:
        logger.error(f"Callback error: {e}")
        response_text = "⚠️ Error processing request."

    # 1. Answer Callback (Stop loading animation)
    requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={
        "callback_query_id": callback_id,
        "text": f"Processing {action}..."
    })
    
    # 2. Edit the message to show final status (remove buttons)
    if message:
        requests.post(f"https://api.telegram.org/bot{token}/editMessageText", json={
            "chat_id": message['chat']['id'],
            "message_id": message['message_id'],
            "text": response_text,
            "parse_mode": "Markdown"
        })
