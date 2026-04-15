from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AdvertiserApplication, Advertisement, PaymentTransaction
import uuid
from .forms import AdvertiserApplicationForm, AdvertisementForm
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import logout
from django.db.models import Count, Sum
from core.models import Profile
from location.models import State, City
from django.core.files.storage import FileSystemStorage

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
            
            # Update role to advertiser
            request.user.role = 'advertiser'
            request.user.save()
            
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
    try:
        application = AdvertiserApplication.objects.get(user=request.user)
    except AdvertiserApplication.DoesNotExist:
        # If they landed here but haven't even applied, send them to the application form
        return redirect('apply_advertiser')
        
    if application.status == 'approved':
        return redirect('advertiser_dashboard')
    
    all_verified = all([
        application.registration_verified,
        application.gst_verified,
        application.pan_verified,
        application.bank_verified
    ])
    
    return render(request, 'ads/advertiser_pending.html', {
        'application': application,
        'all_verified': all_verified
    })

@login_required
def advertiserDashboardView(request):
    # Ensure they are approved
    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')
        
    my_ads = Advertisement.objects.filter(advertiser=request.user).order_by('-created_at')
    
    # Simple stats for overview
    total_campaigns = my_ads.count()
    active_campaigns = my_ads.filter(status='Active').count()
    
    context = {
        'application': application,
        'my_ads': my_ads,
        'stats': {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_impressions': 0, # Placeholders
            'total_clicks': 0
        }
    }
    return render(request, 'ads/advertiser_dashboard_overview.html', context)

@login_required
def advertiserReportsView(request):
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
        'stats': {
            'total_impressions': 0,
            'total_clicks': 0,
            'ctr': 0
        }
    }
    return render(request, 'ads/advertisement_reports.html', context)

@login_required
def advertiserBillingView(request):
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
    }
    return render(request, 'ads/advertisement_billing.html', context)

@login_required
def advertiserWithdrawView(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.role == 'advertiser':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your application has been withdrawn and account deleted.')
    return redirect('home')
@login_required
def advertiserProfileView(request):
    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')
        
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.phone = request.POST.get("phone", user.phone)
        
        profile.bio = request.POST.get("bio", profile.bio)
        state_id = request.POST.get("state")
        city_id = request.POST.get("city")
        if state_id:
            profile.state_id = state_id
        if city_id:
            profile.city_id = city_id
        
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            fs = FileSystemStorage()
            from django.conf import settings
            
            if profile.profile_image:
                old_name = profile.profile_image.replace(settings.MEDIA_URL, "")
                if fs.exists(old_name):
                    fs.delete(old_name)
                    
            filename = fs.save(f"profile_images/{user.id}_{avatar.name}", avatar)
            profile.profile_image = fs.url(filename)
            
        user.save()
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("advertiser_profile")

    states = State.objects.all()
    cities = City.objects.all()
    
    return render(request, "ads/advertiser_profile.html", {
        "states": states,
        "cities": cities,
        "profile": profile,
        "application": application, # needed for sidebar/header
    })

@login_required
def advertiserGeneralView(request):
    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')
        
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "update_notifications" in request.POST:
            profile.email_notifications = request.POST.get("email_notifications") == "on"
            profile.breaking_news_alerts = request.POST.get("breaking_news_alerts") == "on"
            profile.weekly_newsletter = request.POST.get("weekly_newsletter") == "on"
            profile.article_recommendations = request.POST.get("article_recommendations") == "on"
            profile.save()
            messages.success(request, "Notification preferences updated successfully.")
            return redirect("advertiser_general")
            
        elif "update_password" in request.POST:
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password and new_password == confirm_password:
                user = request.user
                user.set_password(new_password)
                user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match.")
            return redirect("advertiser_general")

    return render(request, "ads/advertiser_general.html", {
        "profile": profile,
        "application": application
    })

@login_required
def advertiserCampaignsView(request):
    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')

    my_ads = Advertisement.objects.filter(advertiser=request.user).order_by('-created_at')
    
    return render(request, 'ads/my_campaigns.html', {
        'application': application,
        'my_ads': my_ads
    })

@login_required
def createCampaignView(request):
    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')

    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.advertiser = request.user
            ad.status = 'Active'
            ad.payment_status = 'Pending'
            
            # Calculate duration in minutes from date interval (inclusive)
            if ad.start_date and ad.end_date:
                days = (ad.end_date - ad.start_date).days + 1
                if days < 1: days = 1 # Safety check
                ad.duration_minutes = days * 24 * 60
            else:
                ad.duration_minutes = 0
            
            # Pricing logic as per new changes
            rates = {
                'Homepage Middle': {'Banner': 50, 'Video': 100},
                'Homepage Sidebar': {'Banner': 40, 'Video': 90},
                'Article Details Middle': {'Banner': 35, 'Video': 80},
                'Article Details Sidebar': {'Banner': 30, 'Video': 75},
            }
            
            placement_rates = rates.get(ad.placement, rates['Homepage Middle'])
            daily_rate = placement_rates.get(ad.ad_format, 50)
            ad.amount = days * daily_rate
            
            ad.save()
            messages.success(request, f"Campaign created! Calculated amount: ₹{ad.amount}")
            return redirect('advertiser_campaigns')
    else:
        form = AdvertisementForm()

    return render(request, 'ads/create_campaign.html', {
        'application': application,
        'form': form
    })

@login_required
def editCampaignView(request, id):
    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')

    ad = get_object_or_404(Advertisement, id=id, advertiser=request.user)
    
    # Restriction: Only editable if payment is Pending
    if ad.payment_status != 'Pending':
        messages.error(request, "You cannot edit a campaign once payment is completed.")
        return redirect('advertiser_campaigns')

    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            ad = form.save(commit=False)
            
            # Recalculate duration and amount
            if ad.start_date and ad.end_date:
                days = (ad.end_date - ad.start_date).days + 1
                if days < 1: days = 1
                ad.duration_minutes = days * 24 * 60
                
                # Pricing logic
                rates = {
                    'Homepage Middle': {'Banner': 50, 'Video': 100},
                    'Homepage Sidebar': {'Banner': 40, 'Video': 90},
                    'Article Details Middle': {'Banner': 35, 'Video': 80},
                    'Article Details Sidebar': {'Banner': 30, 'Video': 75},
                }
                placement_rates = rates.get(ad.placement, rates['Homepage Middle'])
                daily_rate = placement_rates.get(ad.ad_format, 50)
                ad.amount = days * daily_rate
            
            ad.save()
            messages.success(request, "Campaign updated successfully!")
            return redirect('advertiser_campaigns')
    else:
        form = AdvertisementForm(instance=ad)

    return render(request, 'ads/create_campaign.html', {
        'application': application,
        'form': form,
        'is_edit': True,
        'ad': ad
    })

@login_required
def initiatePaymentView(request, ad_id):
    application = get_object_or_404(AdvertiserApplication, user=request.user)
    ad = get_object_or_404(Advertisement, id=ad_id, advertiser=request.user)
    
    if ad.payment_status == 'Paid':
        messages.info(request, "This campaign is already paid.")
        return redirect('advertiser_billing')
    
    # Create PENDING transaction
    transaction = PaymentTransaction.objects.create(
        advertisement=ad,
        order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
        status='PENDING',
        amount=ad.amount
    )
    
    return render(request, 'ads/payment_process.html', {
        'ad': ad,
        'transaction': transaction,
        'application': application
    })

@login_required
def paymentSuccessView(request, transaction_id):
    transaction = get_object_or_404(PaymentTransaction, id=transaction_id, advertisement__advertiser=request.user)
    
    transaction.status = 'SUCCESS'
    transaction.payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
    transaction.save()
    
    # Update advertisement payment status
    ad = transaction.advertisement
    ad.payment_status = 'Paid'
    ad.save()
    
    messages.success(request, f"Payment successful! Transaction ID: {transaction.payment_id}")
    return redirect('advertiser_billing')

@login_required
def paymentFailedView(request, transaction_id):
    transaction = get_object_or_404(PaymentTransaction, id=transaction_id, advertisement__advertiser=request.user)
    
    transaction.status = 'FAILED'
    transaction.failure_reason = "Simulated transaction failure."
    transaction.save()
    
    messages.error(request, "Your transaction has failed. Please try again.")
    return redirect('advertiser_billing')
