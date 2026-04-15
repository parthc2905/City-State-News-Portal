from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.applyAdvertiserView, name='apply_advertiser'),
    path('pending/', views.advertiserPendingView, name='advertiser_pending'),
    path('dashboard/', views.advertiserDashboardView, name='advertiser_dashboard'),
    path('campaigns/', views.advertiserCampaignsView, name='advertiser_campaigns'),
    path('campaigns/create/', views.createCampaignView, name='create_campaign'),
    path('campaigns/edit/<int:id>/', views.editCampaignView, name='edit_campaign'),
    path('reports/', views.advertiserReportsView, name='advertiser_reports'),
    path('billing/', views.advertiserBillingView, name='advertiser_billing'),
    path('profile/', views.advertiserProfileView, name='advertiser_profile'),
    path('general/', views.advertiserGeneralView, name='advertiser_general'),
    path('withdraw/', views.advertiserWithdrawView, name='advertiser_withdraw'),
    
    # Payment Routes
    path('payment/initiate/<int:ad_id>/', views.initiatePaymentView, name='payment_initiate'),
    path('payment/success/<int:transaction_id>/', views.paymentSuccessView, name='payment_success'),
    path('payment/failed/<int:transaction_id>/', views.paymentFailedView, name='payment_failed'),
]
