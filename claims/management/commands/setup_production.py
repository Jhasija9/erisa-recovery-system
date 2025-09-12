from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Setup production database'

    def handle(self, *args, **options):
        # Run migrations
        call_command('migrate')
        
        # Create superuser if needed
        call_command('createsuperuser', interactive=False)
        
        self.stdout.write(
            self.style.SUCCESS('Production database setup complete!')
        )
