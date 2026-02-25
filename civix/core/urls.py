from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.userSignupView, name='signup'), 
    path('login/', views.userLoginView, name='login'),
    path('admin/dashboard/', views.adminDashboardView, name='admin_dashboard'),
    path('reader/dashboard/', views.readerDashboardView, name='reader_dashboard'),
]