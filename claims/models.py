from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Claim(models.Model):
    """Main claim record - provided data"""
    id = models.CharField(max_length=20, primary_key=True, help_text="Claim ID")
    patient_name = models.CharField(max_length=255)
    billed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('Denied', 'Denied'),
        ('Under Review', 'Under Review'),
        ('Paid', 'Paid'),
        # ('Pending', 'Pending'),
    ])
    insurer_name = models.CharField(max_length=255)
    discharge_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-discharge_date']

    def __str__(self):
        return f"{self.id} - {self.patient_name}"

    @property
    def underpayment_amount(self):
        """Calculate potential underpayment"""
        return max(0, self.billed_amount - self.paid_amount)

    @property
    def status_color(self):
        """Return CSS class for status styling"""
        colors = {
            'Denied': 'danger',
            'Under Review': 'warning',
            'Paid': 'success',
            # 'Pending': 'info',
        }
        return colors.get(self.status, 'secondary')


class ClaimDetail(models.Model):
    """Detailed claim information - provided data"""
    id = models.AutoField(primary_key=True)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='details')
    cpt_codes = models.TextField(help_text="CPT codes separated by commas")
    denial_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detail for {self.claim.id}"

    @property
    def cpt_codes_list(self):
        """Return CPT codes as a list"""
        if self.cpt_codes:
            return [code.strip() for code in self.cpt_codes.split(',')]
        return []


class UserProfile(models.Model):
    """User profile with role-based permissions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[
        ('admin', 'Admin'),
        ('user', 'User'),
    ], default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_user(self):
        return self.role == 'user'


class Flag(models.Model):
    """Flags for claims - now with real user references"""
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='flags')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Real user
    reason = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Flag for {self.claim.id} by {self.user.username}"

    def resolve(self):
        """Resolve the flag"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()


class Note(models.Model):
    """User-generated notes and annotations - now with real user references"""
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Real user
    content = models.TextField()
    note_type = models.CharField(max_length=50, choices=[
        ('admin', 'Admin Note'),
        ('system', 'System Flag'),
        ('user', 'User Note'),
    ], default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.claim.id} by {self.user.username}"

    @property
    def time_ago(self):
        """Human readable time since creation"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
