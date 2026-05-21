from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import Subscription, SubscriptionTransaction

@login_required
def pricingView(request):
    active_subscription = Subscription.objects.filter(
        user=request.user, 
        status='Active', 
        end_date__gte=timezone.now()
    ).first()
    
    canceled_subscription = Subscription.objects.filter(
        user=request.user,
        status='Canceled',
        end_date__gte=timezone.now()
    ).first()

    return render(request, 'subscriptions/pricing.html', {
        'active_subscription': active_subscription,
        'canceled_subscription': canceled_subscription
    })



@login_required
def initiateSubscriptionPaymentView(request, plan_type):
    # Normalize plan_type
    plan_type = plan_type.capitalize()
    
    if plan_type not in ['Monthly', 'Yearly']:
        messages.error(request, f"Invalid subscription plan: {plan_type}")
        return redirect('subscription_pricing')


    # Pricing mapping
    prices = {
        'Monthly': 99.00,
        'Yearly': 799.00
    }
    amount = prices.get(plan_type)

    # Create a Pending subscription
    subscription = Subscription.objects.create(
        user=request.user,
        plan_type=plan_type,
        status='Pending',
        amount=amount
    )

    # Create a Pending transaction
    transaction = SubscriptionTransaction.objects.create(
        subscription=subscription,
        order_id=f"SUB-ORD-{uuid.uuid4().hex[:8].upper()}",
        status='PENDING',
        amount=amount
    )

    return redirect('subscription_payment_process', transaction_id=transaction.id)

@login_required
def subscriptionPaymentProcessView(request, transaction_id):
    transaction = get_object_or_404(SubscriptionTransaction, id=transaction_id, subscription__user=request.user)
    return render(request, 'subscriptions/payment_process.html', {
        'transaction': transaction,
        'subscription': transaction.subscription
    })

@login_required
def subscriptionPaymentSuccessView(request, transaction_id):
    transaction = get_object_or_404(SubscriptionTransaction, id=transaction_id, subscription__user=request.user)
    
    if transaction.status == 'SUCCESS':
        return redirect('home')

    # Update transaction
    transaction.status = 'SUCCESS'
    transaction.payment_id = f"SUB-PAY-{uuid.uuid4().hex[:12].upper()}"
    transaction.save()

    # Activate subscription
    subscription = transaction.subscription
    subscription.status = 'Active'
    subscription.start_date = timezone.now()
    
    if subscription.plan_type == 'Monthly':
        subscription.end_date = subscription.start_date + timedelta(days=30)
    elif subscription.plan_type == 'Yearly':
        subscription.end_date = subscription.start_date + timedelta(days=365)
    
    subscription.save()

    # Send confirmation email
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = "Welcome to CIVIX Premium!"
        message = f"Hello {request.user.first_name or 'Reader'},\n\nThank you for subscribing to the {subscription.plan_type} plan! Your premium access is now active until {subscription.end_date.strftime('%B %d, %Y')}.\n\nEnjoy an ad-free experience and unlimited access to local news across India.\n\nBest regards,\nThe CIVIX Team"
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Error sending subscription email: {e}")

    messages.success(request, f"Subscription activated successfully! Enjoy premium features until {subscription.end_date.strftime('%B %d, %Y')}.")
    return redirect('home')

@login_required
def cancelSubscriptionView(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    
    if subscription.status == 'Active':
        subscription.status = 'Canceled'
        subscription.save()
        messages.success(request, "Your subscription has been canceled. You will still have access until the end of your billing period.")
    else:
        messages.error(request, "This subscription cannot be canceled.")
        
    return redirect('subscription_pricing')


@login_required
def subscriptionPaymentFailedView(request, transaction_id):
    transaction = get_object_or_404(SubscriptionTransaction, id=transaction_id, subscription__user=request.user)
    
    transaction.status = 'FAILED'
    transaction.failure_reason = "Simulated transaction failure."
    transaction.save()

    messages.error(request, "Payment failed. Please try again or contact support.")
    return redirect('subscription_pricing')
