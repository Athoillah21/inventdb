"""
Vercel serverless handler for Django
This file exports the WSGI application for Vercel's Python runtime.
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# This is the WSGI application that Vercel will use
app = get_wsgi_application()
