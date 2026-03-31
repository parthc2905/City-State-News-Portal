from django import forms
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
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://www.techvision.com'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '29ABCDE1234F1Z5'}),
            'campaign_objectives': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Describe your marketing goals...', 'rows': 4}),
            # target_cities and ad_format_preference will be handled as comma-separated from the frontend checkboxes
            'target_cities': forms.HiddenInput(),
            'ad_format_preference': forms.HiddenInput(),
        }
