from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.models import User
from claims.models import UserProfile

class Command(BaseCommand):
    help = 'Setup Google OAuth and create admin user'

    def handle(self, *args, **options):
        # Clear existing flags and notes
        from claims.models import Flag, Note
        Flag.objects.all().delete()
        Note.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared existing flags and notes'))

        # Get or create the site (don't try to create with specific ID)
        site, created = Site.objects.get_or_create(
            domain='127.0.0.1:8000',
            defaults={'name': 'ERISA Recovery'}
        )
        if not created:
            site.name = 'ERISA Recovery'
            site.save()
        self.stdout.write(self.style.SUCCESS(f'Site {"created" if created else "updated"}: {site.domain}'))

        # Create Google SocialApp
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': 'your-google-client-id.apps.googleusercontent.com',
                'secret': 'your-google-client-secret',
            }
        )
        if not created:
            google_app.client_id = 'your-google-client-id.apps.googleusercontent.com'
            google_app.secret = 'your-google-client-secret'
            google_app.save()
        
        # Add site to the app (remove existing first)
        google_app.sites.clear()
        google_app.sites.add(site)
        self.stdout.write(self.style.SUCCESS(f'Google SocialApp {"created" if created else "updated"}'))

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@erisa.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created: admin/admin123'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))

        # Create UserProfile for admin
        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        if not created:
            admin_profile.role = 'admin'
            admin_profile.save()
        self.stdout.write(self.style.SUCCESS('Admin profile created/updated'))

        self.stdout.write(self.style.SUCCESS('\n✅ Setup complete!'))
        self.stdout.write(self.style.WARNING('⚠️  IMPORTANT: Update Google OAuth credentials in Django Admin'))
        self.stdout.write(self.style.WARNING('   1. Go to: http://127.0.0.1:8000/admin/'))
        self.stdout.write(self.style.WARNING('   2. Login with: admin/admin123'))
        self.stdout.write(self.style.WARNING('   3. Go to Social Applications > Google'))
        self.stdout.write(self.style.WARNING('   4. Update Client ID and Secret with your Google OAuth credentials'))
