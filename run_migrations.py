import os
import django
from django.core.management import execute_from_command_line

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erisa_recovery.settings')
django.setup()

# Run migrations
print("🔄 Running Django migrations...")
execute_from_command_line(['manage.py', 'migrate'])
print("✅ Migrations completed successfully!")
