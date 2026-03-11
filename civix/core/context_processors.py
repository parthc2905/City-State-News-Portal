from django.db.models import Q
from .models import User

def admin_counts(request):
    """Add admin dashboard counts to all templates"""
    if request.user.is_authenticated and request.user.is_admin:
        pending_applications = User.objects.filter(
            role__in=['journalist', 'advertiser'],
            approval_status='pending'
        ).count()
        
        pending_journalists = User.objects.filter(
            role='journalist',
            approval_status='pending'
        ).count()
        
        pending_advertisers = User.objects.filter(
            role='advertiser',
            approval_status='pending'
        ).count()
        
        return {
            'pending_applications': pending_applications,
            'pending_journalists': pending_journalists,
            'pending_advertisers': pending_advertisers,
        }
    return {}