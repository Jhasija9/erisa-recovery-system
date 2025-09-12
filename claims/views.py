from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg, F, Case, When, FloatField
from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import UserCreationForm
from django import forms
from datetime import datetime, timedelta
from collections import Counter
import json
import os
import tempfile
from django.db import connection

from .models import Claim, ClaimDetail, Flag, Note, UserProfile
from .forms import DataUploadForm
from .management.commands.load_claims_data import Command as LoadDataCommand


def admin_required(view_func):
    """Decorator to require admin role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('claims:login')
        try:
            profile = request.user.userprofile
            if not profile.is_admin:
                return render(request, 'claims/not_authorized.html', status=403)
        except UserProfile.DoesNotExist:
            return render(request, 'claims/not_authorized.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with email validation"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")
    
    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        """Validate that username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.create(user=user, role='user')
        return user


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome, {username}!')
                return redirect('claims:claims_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'claims/register.html', {'form': form})


def login_view(request):
    """Custom login view that accepts both username and email"""
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If username authentication fails, try with email
        if user is None:
            try:
                # Find user by email
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user:
            login(request, user)
            # Use the actual username for the welcome message
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect based on role
            try:
                profile = user.userprofile
                if profile.is_admin:
                    return redirect('claims:dashboard')
                else:
                    return redirect('claims:claims_list')
            except UserProfile.DoesNotExist:
                return redirect('claims:claims_list')
        else:
            messages.error(request, 'Invalid username/email or password')
    
    return render(request, 'claims/login.html')


@login_required
def logout_view(request):
    """Logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('claims:login')


def create_user_profile(user):
    """Create user profile for new users (including Google OAuth users)"""
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user, role='user')


@login_required
def claims_list(request):
    """Main claims list view with search, filter, and pagination functionality"""
    # Ensure user has a profile
    create_user_profile(request.user)
    
    claims = Claim.objects.all().order_by('-id')  # Order by newest first
    
    # Search functionality - ONLY patient name and claim ID
    search_query = request.GET.get('search', '')
    if search_query:
        claims = claims.filter(
            Q(patient_name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        claims = claims.filter(status=status_filter)
    
    # Filter by insurer
    insurer_filter = request.GET.get('insurer', '')
    if insurer_filter:
        claims = claims.filter(insurer_name__icontains=insurer_filter)
    
    # Pagination
    per_page = request.GET.get('per_page', 25)
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    paginator = Paginator(claims, per_page)
    page = request.GET.get('page', 1)
    
    try:
        claims_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        claims_page = paginator.page(1)
    
    # Add flag status to each claim for template
    for claim in claims_page:
        claim.has_unresolved_flags = claim.flags.filter(is_resolved=False).exists()
        claim.has_resolved_flags = claim.flags.filter(is_resolved=True).exists()
    
    # Get filter options
    status_choices = [
        ('', 'All Statuses'),
        ('Paid', 'Paid'),
        ('Denied', 'Denied'),
        ('Under Review', 'Under Review'),
    ]
    
    insurers = Claim.objects.values_list('insurer_name', flat=True).distinct().order_by('insurer_name')
    
    context = {
        'claims': claims_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'insurer_filter': insurer_filter,
        'per_page': per_page,
        'status_choices': status_choices,
        'insurers': insurers,
    }
    
    # Check if this is an HTMX request
    if request.headers.get('HX-Request'):
        # Return only the table content for HTMX requests
        return render(request, 'claims/partials/claims_table.html', context)
    else:
        # Return full page for regular requests
        return render(request, 'claims/claims_list.html', context)


@login_required
def claim_detail(request, claim_id):
    """HTMX-powered claim detail view"""
    claim = get_object_or_404(Claim, id=claim_id)
    details = claim.details.first()
    flags = claim.flags.filter(is_resolved=False)
    notes = claim.notes.all()[:10]  # Show last 10 notes
    
    # Get mode parameter (view or edit)
    mode = request.GET.get('mode', 'view')
    is_edit_mode = mode == 'edit'
    
    # Get search parameters from request
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', '1')
    status_filter = request.GET.get('status', '')
    insurer_filter = request.GET.get('insurer', '')
    per_page = request.GET.get('per_page', '25')
    
    # Get resolved flags
    resolved_flags = claim.flags.filter(is_resolved=True)
    
    # Check if claim has active flags
    has_active_flags = flags.exists()
    active_flag = flags.first() if has_active_flags else None
    
    context = {
        'claim': claim,
        'details': details,
        'flags': flags,
        'resolved_flags': resolved_flags,
        'notes': notes,
        'is_edit_mode': is_edit_mode,
        'mode': mode,
        'has_active_flags': has_active_flags,
        'active_flag': active_flag,
        # Add search parameters to context
        'search_query': search_query,
        'page': page,
        'status_filter': status_filter,
        'insurer_filter': insurer_filter,
        'per_page': per_page,
    }
    
    return render(request, 'claims/claim_detail.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def add_flag(request, claim_id):
    """Add a flag to a claim"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            reason = data.get('reason', 'Flagged for review')
        else:
            # Handle form data from HTMX
            reason = request.POST.get('reason', 'Flagged for review')
        
        claim = get_object_or_404(Claim, id=claim_id)
        
        # Check if claim already has an unresolved flag
        existing_flag = claim.flags.filter(is_resolved=False).first()
        if existing_flag:
            return JsonResponse({
                'success': False,
                'message': 'This claim is already flagged. Please resolve the existing flag first.'
            }, status=400)
        
        # Use the authenticated user
        flag = Flag.objects.create(
            claim=claim,
            user=request.user,  # Real authenticated user
            reason=reason
        )
        
        return render(request, 'claims/partials/flag_item.html', {
            'flag': flag
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def add_note(request, claim_id):
    """Add a note to a claim"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            content = data.get('content', '')
            note_type = data.get('note_type', 'user')
        else:
            # Handle form data from HTMX
            content = request.POST.get('content', '')
            note_type = request.POST.get('note_type', 'user')
        claim = get_object_or_404(Claim, id=claim_id)
        
        # Use the authenticated user
        note = Note.objects.create(
            claim=claim,
            user=request.user,  # Real authenticated user
            content=content,
            note_type=note_type
        )
        
        return render(request, 'claims/partials/note_item.html', {
            'note': note
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def resolve_flag(request, claim_id):
    """Resolve a flag for a claim"""
    try:
        claim = get_object_or_404(Claim, id=claim_id)
        active_flag = claim.flags.filter(is_resolved=False).first()
        
        if not active_flag:
            return JsonResponse({
                'success': False,
                'message': 'No active flag found for this claim'
            }, status=400)
        
        # Resolve the flag
        active_flag.is_resolved = True
        active_flag.resolved_at = timezone.now()
        active_flag.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Flag resolved successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@admin_required
def dashboard(request):
    """Enhanced admin dashboard with comprehensive analytics"""
    from .models import Claim, ClaimDetail, Flag, Note
    
    # Get filter parameters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    insurer = request.GET.get('insurer')
    status = request.GET.get('status')
    
    # Base queryset with filters
    claims_qs = Claim.objects.all()
    
    # Apply date filters
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            claims_qs = claims_qs.filter(discharge_date__gte=from_date_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            claims_qs = claims_qs.filter(discharge_date__lte=to_date_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    # Apply insurer filter (use icontains for partial matching)
    if insurer:
        claims_qs = claims_qs.filter(insurer_name__icontains=insurer)
    
    # Apply status filter (handle case sensitivity and "All" option)
    if status and status.lower() != 'all':
        # Convert to proper case
        status_map = {
            'paid': 'Paid',
            'denied': 'Denied', 
            'under review': 'Under Review'
        }
        proper_status = status_map.get(status.lower(), status)
        claims_qs = claims_qs.filter(status=proper_status)
    
    # A) Basic counts
    total_claims = claims_qs.count()
    paid_claims = claims_qs.filter(status='Paid').count()
    denied_claims = claims_qs.filter(status='Denied').count()
    under_review_claims = claims_qs.filter(status='Under Review').count()
    
    # B) Payment rates
    payment_rate = 0
    if total_claims > 0:
        total_billed = claims_qs.aggregate(Sum('billed_amount'))['billed_amount__sum'] or 0
        total_paid = claims_qs.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        payment_rate = (total_paid / total_billed * 100) if total_billed > 0 else 0
    
    # C) Monthly trends (last 6 months) - Database agnostic
    six_months_ago = timezone.now() - timedelta(days=180)

    # Use database-appropriate date function
    if connection.vendor == 'postgresql':
        date_func = "TO_CHAR(discharge_date, 'YYYY-MM-01')"
    else:
        date_func = "strftime('%%Y-%%m-01', discharge_date)"

    monthly_data = claims_qs.filter(discharge_date__gte=six_months_ago).extra(
        select={'month': date_func}
    ).values('month', 'status').annotate(count=Count('id')).order_by('month')
    
    # Calculate payment ratio by month
    payment_ratio_data = claims_qs.filter(discharge_date__gte=six_months_ago).extra(
        select={'month': date_func}
    ).values('month').annotate(
        total_billed=Sum('billed_amount'),
        total_paid=Sum('paid_amount')
    ).annotate(
        payment_ratio=Case(
            When(total_billed__gt=0, then=F('total_paid') * 100.0 / F('total_billed')),
            default=0,
            output_field=FloatField()
        )
    ).order_by('month')
    
    # D) Insurer breakdown
    insurer_data = claims_qs.values('insurer_name', 'status').annotate(count=Count('id'))
    
    # E) CPT codes analysis
    cpt_codes = []
    for detail in ClaimDetail.objects.filter(claim__in=claims_qs):
        cpt_codes.extend(detail.cpt_codes_list)
    top_cpt_codes = Counter(cpt_codes).most_common(10)
    
    # F) Aging analysis (Under Review only)
    now = timezone.now().date()
    aging_buckets = {
        '0-30': claims_qs.filter(status='Under Review', discharge_date__gte=now-timedelta(days=30)).count(),
        '31-60': claims_qs.filter(status='Under Review', discharge_date__gte=now-timedelta(days=60), discharge_date__lt=now-timedelta(days=30)).count(),
        '61-90': claims_qs.filter(status='Under Review', discharge_date__gte=now-timedelta(days=90), discharge_date__lt=now-timedelta(days=60)).count(),
        '90+': claims_qs.filter(status='Under Review', discharge_date__lt=now-timedelta(days=90)).count(),
    }
    
    # G) Flag backlog
    total_flags = Flag.objects.filter(claim__in=claims_qs).count()
    recent_flags = Flag.objects.filter(claim__in=claims_qs, created_at__gte=now-timedelta(days=7)).count()
    
    # H) Recent activity (flags + notes)
    recent_flags_activity = Flag.objects.filter(claim__in=claims_qs).select_related('claim', 'user').order_by('-created_at')[:5]
    recent_notes_activity = Note.objects.filter(claim__in=claims_qs).select_related('claim', 'user').order_by('-created_at')[:5]
    
    # Combine and sort recent activity
    recent_activity = []
    for flag in recent_flags_activity:
        recent_activity.append({
            'type': 'flag',
            'claim_id': flag.claim.id,
            'user': flag.user.username,
            'content': flag.reason[:50] + '...' if len(flag.reason) > 50 else flag.reason,
            'created_at': flag.created_at.isoformat(),
            'created_at_human': flag.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'is_resolved': flag.is_resolved
        })
    for note in recent_notes_activity:
        recent_activity.append({
            'type': 'note',
            'claim_id': note.claim.id,
            'user': note.user.username,
            'content': note.content[:50] + '...' if len(note.content) > 50 else note.content,
            'created_at': note.created_at.isoformat(),
            'created_at_human': note.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'note_type': note.note_type
        })
    
    recent_activity.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activity = recent_activity[:10]
    
    # I) Top underpayment (Paid claims only)
    top_underpayment = claims_qs.filter(status='Paid').annotate(
        underpayment=F('billed_amount') - F('paid_amount')
    ).filter(underpayment__gt=0).order_by('-underpayment')[:10]
    
    # K) Get unique insurers and statuses for filters - ALWAYS get from ALL claims, not filtered
    all_insurers = Claim.objects.values_list('insurer_name', flat=True).distinct().order_by('insurer_name')
    statuses = ['All', 'Paid', 'Denied', 'Under Review']
    
    context = {
        # Basic counts
        'total_claims': total_claims,
        'paid_claims': paid_claims,
        'denied_claims': denied_claims,
        'under_review_claims': under_review_claims,
        
        # Rates
        'payment_rate': round(payment_rate, 1),
        'denial_rate': round((denied_claims / total_claims * 100) if total_claims > 0 else 0, 1),
        
        # Monthly data for charts
        'monthly_data': list(monthly_data),
        
        # Breakdowns
        'insurer_data': list(insurer_data),
        'top_cpt_codes': top_cpt_codes,
        
        # Operational
        'aging_buckets': aging_buckets,
        'total_flags': total_flags,
        'recent_flags': recent_flags,
        'recent_activity': recent_activity,
        
        # Spotlight
        'top_underpayment': top_underpayment,
        
        # Filters - use all_insurers for dropdown options
        'insurers': all_insurers,
        'statuses': statuses,
        'current_filters': {
            'from_date': from_date,
            'to_date': to_date,
            'insurer': insurer,
            'status': status,
        }
    }
    
    # Serialize data for JavaScript - convert to basic Python types
    monthly_data_list = list(monthly_data)
    insurer_data_list = list(insurer_data)
    payment_ratio_list = list(payment_ratio_data)
    
    context['monthly_data_json'] = json.dumps([
        {
            'month': item['month'],
            'status': item['status'],
            'count': item['count']
        } for item in monthly_data_list
    ])
    context['insurer_data_json'] = json.dumps([
        {
            'insurer_name': item['insurer_name'],
            'status': item['status'],
            'count': item['count']
        } for item in insurer_data_list
    ])
    context['payment_ratio_json'] = json.dumps([
        {
            'month': item['month'],
            'payment_ratio': round(float(item['payment_ratio']), 1)
        } for item in payment_ratio_list
    ])
    context['top_cpt_codes_json'] = json.dumps(top_cpt_codes)
    context['recent_activity_json'] = json.dumps(recent_activity)
    
    return render(request, 'claims/dashboard.html', context)


@login_required
@admin_required
def data_upload(request):
    """Data upload view for CSV/JSON files - Admin only"""
    if request.method == 'POST':
        form = DataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get form data
                claims_file = request.FILES.get('claims_file')
                details_file = request.FILES.get('details_file')
                file_format = form.cleaned_data['file_format']
                clear_existing = form.cleaned_data['clear_existing']
                
                # Load claims data first
                if claims_file:
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=f'.{file_format}') as temp_file:
                        for chunk in claims_file.chunks():
                            temp_file.write(chunk)
                        claims_temp_path = temp_file.name
                    
                    # Load claims data
                    load_command = LoadDataCommand()
                    load_command.handle(
                        file=claims_temp_path,
                        format=file_format,
                        clear=clear_existing
                    )
                    os.unlink(claims_temp_path)
                
                # Load details data if provided
                if details_file:
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=f'.{file_format}') as temp_file:
                        for chunk in details_file.chunks():
                            temp_file.write(chunk)
                        details_temp_path = temp_file.name
                    
                    # Load details data
                    from django.core.management import call_command
                    call_command('load_claim_details', file=details_temp_path, format=file_format, clear=clear_existing)
                    os.unlink(details_temp_path)
                
                # Success message
                files_loaded = []
                if claims_file:
                    files_loaded.append(f'Claims: {claims_file.name}')
                if details_file:
                    files_loaded.append(f'Details: {details_file.name}')
                
                messages.success(request, f'Successfully loaded: {", ".join(files_loaded)}')
                return redirect('claims:dashboard')
                
            except Exception as e:
                messages.error(request, f'Error loading data: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DataUploadForm()
    
    context = {
        'form': form,
        'total_claims': Claim.objects.count(),
    }
    
    return render(request, 'claims/data_upload.html', context)


def not_authorized(request):
    """Not authorized page for users without proper permissions"""
    return render(request, 'claims/not_authorized.html', status=403)
