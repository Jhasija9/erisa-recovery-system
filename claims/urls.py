from django.urls import path
from . import views

app_name = 'claims'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('not-authorized/', views.not_authorized, name='not_authorized'),
    
    # Main application URLs
    path('', views.claims_list, name='claims_list'),
    path('claim/<str:claim_id>/', views.claim_detail, name='claim_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.data_upload, name='data_upload'),
    
    # Action URLs
    path('claim/<int:claim_id>/flag/', views.add_flag, name='add_flag'),
    path('claim/<int:claim_id>/note/', views.add_note, name='add_note'),
    path('claim/<int:claim_id>/resolve-flag/', views.resolve_flag, name='resolve_flag'),
]
