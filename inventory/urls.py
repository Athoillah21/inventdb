from django.urls import path
from . import views
from . import webhook_view

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/dashboard-data/', views.dashboard_api, name='dashboard_api'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/check-auth/', views.api_check_auth, name='api_check_auth'),
    path('inventory/', views.InventoryListView.as_view(), name='inventory_list'),
    path('inventory/export/', views.export_inventory_csv, name='inventory_export'),
    path('inventory/add/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('inventory/<int:pk>/edit/', views.InventoryUpdateView.as_view(), name='inventory_update'),
    path('inventory/<int:pk>/delete/', views.InventoryDeleteView.as_view(), name='inventory_delete'),
    
    # Svelte API Endpoints
    path('api/inventory/', views.api_inventory_list, name='api_inventory_list'),
    path('api/inventory/create/', views.api_inventory_create, name='api_inventory_create'),
    path('api/inventory/<int:pk>/update/', views.api_inventory_update, name='api_inventory_update'),
    path('api/inventory/<int:pk>/delete/', views.api_inventory_delete, name='api_inventory_delete'),
    
    # Telegram Webhook
    path('api/telegram/webhook/', webhook_view.telegram_webhook, name='telegram_webhook'),
]
