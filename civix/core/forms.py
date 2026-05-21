from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.validators import RegexValidator
from .models import User, Profile, JournalistApplication

# User Registration Form
class UserSignupForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^[A-Za-z]+$', message='First name must contain only letters.')],
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "John",
            "pattern": "[A-Za-z]+",
            "title": "First name should only contain letters."
        })
    )

    last_name = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^[A-Za-z]+$', message='Last name must contain only letters.')],
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Doe",
            "pattern": "[A-Za-z]+",
            "title": "Last name should only contain letters."
        })
    )

    email = forms.EmailField(
        required=True,
        error_messages={'invalid': 'Enter a valid email address.', 'required': 'Email is required.'},
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'id' : 'signupEmail',
            'pattern': '^[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}$',
            'title': 'Please enter a valid email format (e.g. user@domain.com).'
        })
    )

    phone_number = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^[1-9][0-9]{9}$', message='Enter a valid 10‑digit phone number not starting with 0.')],
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "9876543210",
            "type": "tel",
            "pattern": "[1-9][0-9]{9}",
            "title": "Phone number must be exactly 10 digits and cannot start with 0."
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

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    password1 = forms.CharField(
        required=True,
        min_length=8,
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "id": "signupPassword",
            "placeholder": "••••••••",
            "minlength": "8",
            "onkeyup": "checkPasswordStrength()"
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
        error_messages={'invalid': 'Enter a valid email address.', 'required': 'Email is required.'},
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'id' : 'signupEmail',
            'pattern': '^[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}$',
            'title': 'Please enter a valid email format (e.g. user@domain.com).'
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

# Comment Form
class CommentForm(forms.Form):
    comment_text = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "comment-textarea",
            "placeholder": "Enter your comment...",
            "rows": 4
        })
    )


class JournalistIdentityForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^[A-Za-z]+$', message='First name must contain only letters.')],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "pattern": "[A-Za-z]+",
            "title": "First name should only contain letters."
        })
    )
    last_name = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^[A-Za-z]+$', message='Last name must contain only letters.')],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "pattern": "[A-Za-z]+",
            "title": "Last name should only contain letters."
        })
    )
    phone = forms.CharField(
        required=True,
        validators=[RegexValidator(regex=r'^[1-9][0-9]{9}$', message='Enter a valid 10‑digit phone number not starting with 0.')],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "type": "tel",
            "pattern": "[1-9][0-9]{9}",
            "title": "Phone number must be exactly 10 digits and cannot start with 0."
        })
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone"]

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone.replace(" ", "").replace("-", "")
            if not phone.isdigit() or len(phone) != 10 or phone.startswith('0'):
                raise forms.ValidationError("Enter a valid 10-digit phone number not starting with 0.")
        return phone


class JournalistProfileLocationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["state", "city"]


class JournalistApplicationDocumentsForm(forms.ModelForm):
    remove_portfolio = forms.BooleanField(required=False)
    remove_presscard = forms.BooleanField(required=False)
    remove_recommendation = forms.BooleanField(required=False)

    class Meta:
        model = JournalistApplication
        fields = [
            "aadhaar_file",
            "portfolio_file",
            "press_card_file",
            "recommendation_file",
        ]

    def clean(self):
        cleaned_data = super().clean()
        aadhaar = cleaned_data.get('aadhaar_file')
        portfolio = cleaned_data.get('portfolio_file')
        presscard = cleaned_data.get('press_card_file')
        recommendation = cleaned_data.get('recommendation_file')

        for file in [aadhaar, portfolio, presscard, recommendation]:
            if file:
                if file.size > 10 * 1024 * 1024:
                    raise forms.ValidationError(f"File {file.name} is too large. Max size is 10MB.")
                
                valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.zip']
                import os
                ext = os.path.splitext(file.name)[1].lower()
                if ext not in valid_extensions:
                    raise forms.ValidationError(f"File {file.name} has an invalid extension. Allowed: {', '.join(valid_extensions)}")
        
        return cleaned_data


class ForgotPasswordEmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your registered email'
        })
    )

class OTPVerifyForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 6-digit OTP',
            'pattern': '[0-9]{6}'
        })
    )

class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(
        required=True,
        min_length=8,
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "id": "newPassword",
            "placeholder": "••••••••",
            "minlength": "8"
        })
    )
    password2 = forms.CharField(
        required=True,
        min_length=8,
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "id": "confirmNewPassword",
            "placeholder": "••••••••",
            "minlength": "8"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

