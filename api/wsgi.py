import os
import sys
from pathlib import Path

# Set up the environment
project_root = Path(__file__).parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erisa_recovery.settings')
os.environ.setdefault('VERCEL', 'true')

# Import Django
import django
from django.conf import settings

# Configure Django
if not settings.configured:
    django.setup()

# Import WSGI application
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()

# Vercel handler
def handler(request, response):
    """Main handler for Vercel"""
    return application(request, response)

# Alternative handler name
app = handler
