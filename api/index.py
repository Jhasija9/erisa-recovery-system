from django.core.wsgi import get_wsgi_application
import os

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erisa_recovery.settings')

# Get the WSGI application
application = get_wsgi_application()

# Vercel expects a 'handler' variable
handler = application