from django.urls import path
from .views import userSignupView

urlpatterns = [
    path('signup/', userSignupView, name='signup'), 
]