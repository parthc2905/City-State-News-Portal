from django.db.models import Q
from .models import User
from location.models import State

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

from news.models import Category

def global_categories(request):
    try:
        categories = list(Category.objects.all().order_by('category_name'))

        nav_categories = categories[:8]          # first 6
        dropdown_categories = categories[8:]     # remaining

        return {
            'nav_categories': nav_categories,
            'dropdown_categories': dropdown_categories
        }

    except Exception as e:
        print("====== ERROR IN CONTEXT PROCESSOR ======", repr(e))
        return {
            'nav_categories': [],
            'dropdown_categories': []
        }

def all_states(request):
    try:
        states = State.objects.all().order_by('state_name')
        return {
            'all_states': states
        }
    except Exception as e:
        print("====== ERROR IN all_states CONTEXT PROCESSOR ======", repr(e))
        return {
            'all_states': []
        }