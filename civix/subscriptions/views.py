from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import Subscription, SubscriptionTransaction

@login_required
def pricingView(request):
    return render(request, 'subscriptions/pricing.html')

@login_required
def initiateSubscriptionPaymentView(request, plan_type):
    if plan_type not in ['Monthly', 'Yearly']:
        messages.error(request, "Invalid subscription plan.")
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

    messages.success(request, f"Subscription activated successfully! Enjoy premium features until {subscription.end_date.strftime('%B %d, %Y')}.")
    return redirect('home')

@login_required
def subscriptionPaymentFailedView(request, transaction_id):
    transaction = get_object_or_404(SubscriptionTransaction, id=transaction_id, subscription__user=request.user)
    
    transaction.status = 'FAILED'
    transaction.failure_reason = "Simulated transaction failure."
    transaction.save()

    messages.error(request, "Payment failed. Please try again or contact support.")
    return redirect('subscription_pricing')
