from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Sets the Telegram Webhook to the specified domain.'

    def add_arguments(self, parser):
        parser.add_argument('domain', type=str, help='The domain of your Vercel app (e.g., https://myapp.vercel.app)')

    def handle(self, *args, **kwargs):
        domain = kwargs['domain'].rstrip('/')
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        
        if not token:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_TOKEN not found in settings.'))
            return

        webhook_url = f"{domain}/api/telegram/webhook/"
        api_url = f"https://api.telegram.org/bot{token}/setWebhook"
        
        self.stdout.write(f"Setting webhook to: {webhook_url}")
        
        try:
            response = requests.post(api_url, data={'url': webhook_url})
            data = response.json()
            
            if data.get('ok'):
                self.stdout.write(self.style.SUCCESS(f"Successfully set webhook: {data.get('description')}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to set webhook: {data.get('description')}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
