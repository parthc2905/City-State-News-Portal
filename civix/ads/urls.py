from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.applyAdvertiserView, name='apply_advertiser'),
    path('pending/', views.advertiserPendingView, name='advertiser_pending'),
    path('dashboard/', views.advertiserDashboardView, name='advertiser_dashboard'),
    path('campaigns/', views.advertiserCampaignsView, name='advertiser_campaigns'),
    path('campaigns/create/', views.createCampaignView, name='create_campaign'),
    path('reports/', views.advertiserReportsView, name='advertiser_reports'),
    path('billing/', views.advertiserBillingView, name='advertiser_billing'),
    path('profile/', views.advertiserProfileView, name='advertiser_profile'),
    path('general/', views.advertiserGeneralView, name='advertiser_general'),
    path('withdraw/', views.advertiserWithdrawView, name='advertiser_withdraw'),
]
