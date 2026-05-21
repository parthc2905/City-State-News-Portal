from django.db import models
from django.conf import settings

# Create your models here.
class Advertisement(models.Model):
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ads")
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, blank=True)
    target_url = models.URLField(max_length=500, null=True, blank=True)
    media_file = models.FileField(upload_to='advertisements/media/', null=True, blank=True)
    AD_FORMAT_CHOICES = (
        ('Banner', 'Banner image'),
        ('Video', 'Video ad'),
    )
    ad_format = models.CharField(max_length=20, choices=AD_FORMAT_CHOICES, default='Banner')
    PLACEMENT_CHOICES = (
        ('Homepage Middle', 'Homepage Middle'),
        ('Homepage Sidebar', 'Homepage Sidebar'),
        ('Article Details Middle', 'Article Details Middle'),
        ('Article Details Sidebar', 'Article Details Sidebar'),
    )
    placement = models.CharField(max_length=50, choices=PLACEMENT_CHOICES, default='Homepage Middle')
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Expired', 'Expired'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    PAYMENT_STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    duration_minutes = models.PositiveIntegerField(default=5, help_text="Duration in minutes (e.g., 5, 10, 15...)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    impressions_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    hovers_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "advertisement"

    def __str__(self):
        return self.title


class AdvertiserApplication(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advertiser_application')
    
    # Company Info
    company_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    company_size = models.CharField(max_length=50)
    contact_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(max_length=500, null=True, blank=True)
    gst_number = models.CharField(max_length=50)
    
    # Campaign Details
    budget_range = models.CharField(max_length=100)
    campaign_duration = models.CharField(max_length=100)
    target_cities = models.TextField(help_text="Comma-separated cities")
    ad_format_preference = models.TextField(help_text="Comma-separated formats", null=True, blank=True)
    campaign_objectives = models.TextField()
    
    # Documents
    registration_certificate = models.FileField(upload_to='advertiser_docs/registration/')
    gst_certificate = models.FileField(upload_to='advertiser_docs/gst/')
    pan_card = models.FileField(upload_to='advertiser_docs/pan/')
    bank_details = models.FileField(upload_to='advertiser_docs/bank/')
    
    # Verification Flags
    registration_verified = models.BooleanField(default=False)
    gst_verified = models.BooleanField(default=False)
    pan_verified = models.BooleanField(default=False)
    bank_verified = models.BooleanField(default=False)
    
    # Application Info
    choice = (("pending", "pending"), ("approved", "approved"), ("rejected", "rejected"))
    status = models.CharField(max_length=20, choices=choice, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "advertiser_application"

    def __str__(self):
        return f"Advertiser Application: {self.company_name} ({self.user.email})"


class PaymentTransaction(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="transactions")
    
    order_id = models.CharField(max_length=255, null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    
    STATUS_CHOICES = (
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
        ('PENDING', 'PENDING'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    failure_reason = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_transaction"

    def __str__(self):
        return f"Transaction {self.id}: {self.status} for {self.advertisement.title}"
