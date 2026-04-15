from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AdvertiserApplication, Advertisement, PaymentTransaction
import uuid
from .forms import AdvertiserApplicationForm, AdvertisementForm
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import logout
from django.db.models import Count, Sum, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models import Profile
from location.models import State, City
from django.core.files.storage import FileSystemStorage
from datetime import timedelta
import csv

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
    total_impressions = my_ads.aggregate(total=Sum('impressions_count'))['total'] or 0
    total_clicks = my_ads.aggregate(total=Sum('clicks_count'))['total'] or 0
    
    context = {
        'application': application,
        'my_ads': my_ads,
        'stats': {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
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
    aggregates = my_ads.aggregate(
        total_impressions=Sum('impressions_count'),
        total_clicks=Sum('clicks_count'),
        total_hovers=Sum('hovers_count'),
        total_spend=Sum('amount'),
    )
    total_impressions = aggregates['total_impressions'] or 0
    total_clicks = aggregates['total_clicks'] or 0
    total_hovers = aggregates['total_hovers'] or 0
    total_interactions = total_clicks + total_hovers
    ctr = round((total_clicks / total_impressions) * 100, 2) if total_impressions else 0
    engagement_rate = round((total_interactions / total_impressions) * 100, 2) if total_impressions else 0
    
    context = {
        'application': application,
        'my_ads': my_ads,
        'stats': {
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_hovers': total_hovers,
            'total_interactions': total_interactions,
            'ctr': ctr,
            'engagement_rate': engagement_rate,
            'total_spend': aggregates['total_spend'] or 0,
        }
    }
    return render(request, 'ads/advertisement_reports.html', context)


@login_required
def advertiserDownloadReportView(request):
    scope = request.GET.get('scope', 'all')
    if scope not in {'all', 'last_30_days'}:
        scope = 'all'

    try:
        application = request.user.advertiser_application
        if application.status != 'approved':
            return redirect('advertiser_pending')
    except AdvertiserApplication.DoesNotExist:
        return redirect('apply_advertiser')

    ads_qs = Advertisement.objects.filter(advertiser=request.user).order_by('-created_at')
    label = 'all'
    if scope == 'last_30_days':
        cutoff = timezone.now() - timedelta(days=30)
        ads_qs = ads_qs.filter(created_at__gte=cutoff)
        label = 'last_30_days'

    filename = f"civix_ad_report_{label}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Scope',
        'Company Name',
        'Generated At',
    ])
    writer.writerow([
        'Last 30 Days' if scope == 'last_30_days' else 'All Time',
        application.company_name,
        timezone.localtime().strftime('%d %b %Y %I:%M %p'),
    ])
    writer.writerow([])
    writer.writerow([
        'Campaign ID',
        'Campaign Title',
        'Placement',
        'Ad Format',
        'Campaign Status',
        'Payment Status',
        'Created At',
        'Impressions',
        'Clicks',
        'Hovers',
        'Total Interactions',
        'CTR (%)',
        'Engagement Rate (%)',
        'Amount (INR)',
        'Latest Successful Payment ID',
        'Latest Successful Payment Date',
    ])

    for ad in ads_qs:
        interactions = ad.clicks_count + ad.hovers_count
        ctr = round((ad.clicks_count / ad.impressions_count) * 100, 2) if ad.impressions_count else 0
        engagement_rate = round((interactions / ad.impressions_count) * 100, 2) if ad.impressions_count else 0
        latest_success_txn = (
            PaymentTransaction.objects
            .filter(advertisement=ad, status='SUCCESS')
            .order_by('-created_at')
            .first()
        )
        writer.writerow([
            ad.id,
            ad.title,
            ad.placement,
            ad.ad_format,
            ad.status,
            ad.payment_status,
            timezone.localtime(ad.created_at).strftime('%d %b %Y %I:%M %p'),
            ad.impressions_count,
            ad.clicks_count,
            ad.hovers_count,
            interactions,
            ctr,
            engagement_rate,
            ad.amount,
            latest_success_txn.payment_id if latest_success_txn else '-',
            timezone.localtime(latest_success_txn.created_at).strftime('%d %b %Y %I:%M %p') if latest_success_txn else '-',
        ])

    return response


@require_POST
@csrf_exempt
def trackAdEngagementView(request):
    ad_id = request.POST.get('ad_id')
    event_type = request.POST.get('event_type')

    if not ad_id or event_type not in {'impression', 'click', 'hover'}:
        return JsonResponse({'ok': False, 'error': 'Invalid payload'}, status=400)

    ad = Advertisement.objects.filter(
        id=ad_id,
        payment_status='Paid',
        status='Active',
    ).first()
    if not ad:
        return JsonResponse({'ok': False, 'error': 'Ad not found'}, status=404)

    if event_type == 'impression':
        update_field = 'impressions_count'
    elif event_type == 'click':
        update_field = 'clicks_count'
    else:
        update_field = 'hovers_count'
    Advertisement.objects.filter(id=ad.id).update(**{update_field: F(update_field) + 1})
    return JsonResponse({'ok': True})

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


@login_required
def downloadReceiptView(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id, advertiser=request.user)
    transaction = (
        PaymentTransaction.objects
        .filter(advertisement=ad, status='SUCCESS')
        .order_by('-created_at')
        .first()
    )

    if not transaction:
        messages.error(request, "Receipt is available only for successful transactions.")
        return redirect('advertiser_billing')

    application = get_object_or_404(AdvertiserApplication, user=request.user)
    context = {
        'ad': ad,
        'transaction': transaction,
        'application': application,
    }
    return render(request, 'ads/payment_receipt.html', context)
