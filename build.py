#!/usr/bin/env python
"""Build script for Vercel deployment"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erisa_recovery.settings')

# Import Django
import django
django.setup()

# Run migrations
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate'])

# Collect static files
execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])

print("Build completed successfully!")
