#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erisa_recovery.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


# Vercel entry point - this is what Vercel needs
def handler(request, response):
    """Vercel handler function."""
    from django.core.wsgi import get_wsgi_application
    from django.http import HttpResponse
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erisa_recovery.settings')
    
    # Get the WSGI application
    application = get_wsgi_application()
    
    # Handle the request
    return application(request, response)


# For Vercel compatibility
app = handler

if __name__ == "__main__":
    main()
