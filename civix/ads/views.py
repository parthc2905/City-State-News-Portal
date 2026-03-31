from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AdvertiserApplication, Advertisement
from .forms import AdvertiserApplicationForm
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import logout

@login_required
def applyAdvertiserView(request):
    # Check if user already has an application
    try:
        application = request.user.advertiser_application
        if application.status == 'approved':
            return redirect('advertiser_dashboard')
        # If pending and not in edit mode, redirect to pending page
        if application.status == 'pending' and not request.GET.get('edit'):
            return redirect('advertiser_pending')
        # if rejected, allow them to re-apply / edit
    except AdvertiserApplication.DoesNotExist:
        application = None

    if request.method == 'POST':
        form = AdvertiserApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.status = 'pending'
            app.submitted_at = timezone.now()
            app.save()
            messages.success(request, "Your application has been submitted and is under review.")
            return redirect('advertiser_pending')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdvertiserApplicationForm(instance=application)

    return render(request, 'ads/apply_advertiser.html', {'form': form, 'application': application})

@login_required
def advertiserPendingView(request):
    application = get_object_or_404(AdvertiserApplication, user=request.user)
    if application.status == 'approved':
        return redirect('advertiser_dashboard')
    return render(request, 'ads/advertiser_pending.html', {'application': application})

@login_required
def advertiserDashboardView(request):
    # Ensure they are approved
    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')
        
    my_ads = Advertisement.objects.filter(advertiser=request.user)
    
    context = {
        'application': application,
        'my_ads': my_ads,
        # Stats could be added here later
    }
    return render(request, 'ads/advertiser_dashboard.html', context)

@login_required
def advertiserWithdrawView(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.role == 'advertiser':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your application has been withdrawn and account deleted.')
    return redirect('home')
