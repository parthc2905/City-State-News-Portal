from django.urls import path
from . import views
from django.shortcuts import redirect
urlpatterns = [
    path('', views.homePage, name='home'),
    path('signup/', views.userSignupView, name='signup'), 
    path('login/', views.userLoginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('adminpanel/dashboard/', views.adminPanelDashboardView, name='admin_panel_dashboard'),
    path('reader/dashboard/', views.readerDashboardView, name='reader_dashboard'),
    
]