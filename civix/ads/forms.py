from django import forms
from django.core.validators import RegexValidator
from .models import AdvertiserApplication

class AdvertiserApplicationForm(forms.ModelForm):
    # Using multiple checkboxes for target cities if preferred, but for now we follow the diagram
    # The diagram has checkboxes for Mumbai, Delhi, Bengaluru, etc.
    # We can handle this by having a comma-separated string in target_cities
    
    BUSINESS_TYPES = (
        ('', 'Select Business Type'),
        ('Technology / SaaS', 'Technology / SaaS'),
        ('E-commerce', 'E-commerce'),
        ('Real Estate', 'Real Estate'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Food & Beverage', 'Food & Beverage'),
        ('Retail', 'Retail'),
        ('Automotive', 'Automotive'),
        ('Financial Services', 'Financial Services'),
        ('Other', 'Other'),
    )
    
    COMPANY_SIZES = (
        ('', 'Select Company Size'),
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    )
    
    BUDGET_RANGES = (
        ('', 'Select Budget Range'),
        ('10000-25000', '₹10,000 - ₹25,000'),
        ('25000-50000', '₹25,000 - ₹50,000'),
        ('50000-100000', '₹50,000 - ₹1,00,000'),
        ('100000-250000', '₹1,00,000 - ₹2,50,000'),
        ('250000+', '₹2,50,000+'),
    )
    
    DURATIONS = (
        ('', 'Select Duration'),
        ('1', '1 Month'),
        ('3', '3 Months'),
        ('6', '6 Months'),
        ('12', '12 Months'),
        ('ongoing', 'Ongoing'),
    )

    business_type = forms.ChoiceField(choices=BUSINESS_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))
    company_size = forms.ChoiceField(choices=COMPANY_SIZES, widget=forms.Select(attrs={'class': 'form-select'}))
    budget_range = forms.ChoiceField(choices=BUDGET_RANGES, widget=forms.Select(attrs={'class': 'form-select'}))
    campaign_duration = forms.ChoiceField(choices=DURATIONS, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = AdvertiserApplication
        fields = [
            'company_name', 'business_type', 'company_size', 
            'contact_name', 'designation', 'email', 'phone', 
            'website', 'gst_number', 'budget_range', 'campaign_duration',
            'target_cities', 'ad_format_preference', 'campaign_objectives',
            'registration_certificate', 'gst_certificate', 'pan_card', 'bank_details'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'TechVision Solutions Pvt Ltd'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Amit Sharma'}),
            'designation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Marketing Manager'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contact@techvision.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '9876543210', 'pattern': '[1-9][0-9]{9}', 'title': 'Phone number must be exactly 10 digits and cannot start with 0.'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://www.techvision.com'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '29ABCDE1234F1Z5', 'pattern': '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', 'title': 'Enter a valid 15-digit GST number.'}),
            'campaign_objectives': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Describe your marketing goals...', 'rows': 4}),
            # target_cities and ad_format_preference will be handled as comma-separated from the frontend checkboxes
            'target_cities': forms.HiddenInput(),
            'ad_format_preference': forms.HiddenInput(),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone.replace(" ", "").replace("-", "")
            if not phone.isdigit() or len(phone) != 10 or phone.startswith('0'):
                raise forms.ValidationError("Enter a valid 10-digit phone number not starting with 0.")
        return phone

    def clean_gst_number(self):
        gst = self.cleaned_data.get('gst_number')
        if gst:
            import re
            pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
            if not re.match(pattern, gst.upper()):
                raise forms.ValidationError("Enter a valid 15-digit GST identification number.")
        return gst.upper()

    def clean(self):
        cleaned_data = super().clean()
        registration_certificate = cleaned_data.get('registration_certificate')
        gst_certificate = cleaned_data.get('gst_certificate')
        pan_card = cleaned_data.get('pan_card')
        bank_details = cleaned_data.get('bank_details')

        for file in [registration_certificate, gst_certificate, pan_card, bank_details]:
            if file:
                if file.size > 10 * 1024 * 1024:
                    raise forms.ValidationError(f"File {file.name} is too large. Max size is 10MB.")
                if not file.name.lower().endswith('.pdf'):
                    raise forms.ValidationError(f"File {file.name} must be a PDF.")
        
        return cleaned_data

from .models import Advertisement

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'target_url', 'media_file', 'ad_format', 'placement', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Summer Sale 2026'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Brief description of the ad campaign...', 'rows': 3}),
            'target_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://www.yourwebsite.com/sale'}),
            'media_file': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*,video/*'}),
            'ad_format': forms.Select(attrs={'class': 'form-select'}),
            'placement': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
