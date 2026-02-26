from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms

# User Registration Form
class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'role')
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }


# User Login Form
class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())