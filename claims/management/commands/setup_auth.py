from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from claims.models import UserProfile, Flag, Note

class Command(BaseCommand):
    help = 'Setup authentication system and clear test data'

    def handle(self, *args, **options):
        # Clear existing flags and notes
        self.stdout.write('Clearing existing flags and notes...')
        Flag.objects.all().delete()
        Note.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared flags and notes'))

        # Create default admin user
        admin_username = 'admin'
        admin_email = 'admin@erisa-recovery.com'
        admin_password = 'admin123'

        if not User.objects.filter(username=admin_username).exists():
            admin_user = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                is_staff=True,
                is_superuser=True
            )
            
            # Create admin profile
            UserProfile.objects.create(user=admin_user, role='admin')
            
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_username} / {admin_password}'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        self.stdout.write(self.style.SUCCESS('Authentication setup complete!'))
        self.stdout.write('You can now:')
        self.stdout.write('1. Login as admin: admin / admin123')
        self.stdout.write('2. Register new users')
        self.stdout.write('3. Use the system with role-based access')
