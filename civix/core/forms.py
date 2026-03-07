from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User

# User Registration Form
class UserSignupForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "John"
        })
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Doe"
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'id' : 'signupEmail'
        })
    )

    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "9876543210",
            "type": "tel",
            "pattern": "[6-9][0-9]{9}"
        })
    )
    
    role_choice =(
        ('', 'Select Role'),
        ('reader','reader'),
        ('journalist','journalist'),
        ('advertiser','advertiser'),
    )
    role = forms.ChoiceField(
        choices=role_choice,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=True
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "id": "signupPassword",
            "placeholder": "••••••••",
            "minlength": "8",
            "oninput": "checkPasswordStrength()"
        })
    )

    password2 = forms.CharField(
        required=True,
        min_length=8,
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "id": "confirmPassword",
            "placeholder": "••••••••",
            "minlength": "8"
        })
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "password1",
            "password2",
        )

# User Login Form
class UserLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'id' : 'signupEmail'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            'placeholder': "••••••••",
            "id": "signinPassword"
        })
    )