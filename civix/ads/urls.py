from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.applyAdvertiserView, name='apply_advertiser'),
    path('pending/', views.advertiserPendingView, name='advertiser_pending'),
    path('dashboard/', views.advertiserDashboardView, name='advertiser_dashboard'),
    path('withdraw/', views.advertiserWithdrawView, name='advertiser_withdraw'),
]
