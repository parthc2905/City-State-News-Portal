from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricingView, name='subscription_pricing'),
    path('initiate/<str:plan_type>/', views.initiateSubscriptionPaymentView, name='initiate_subscription_payment'),
    path('process/<int:transaction_id>/', views.subscriptionPaymentProcessView, name='subscription_payment_process'),
    path('success/<int:transaction_id>/', views.subscriptionPaymentSuccessView, name='subscription_payment_success'),
    path('failed/<int:transaction_id>/', views.subscriptionPaymentFailedView, name='subscription_payment_failed'),
    path('cancel/<int:subscription_id>/', views.cancelSubscriptionView, name='cancel_subscription'),
]

