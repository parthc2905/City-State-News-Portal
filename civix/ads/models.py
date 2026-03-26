from django.db import models
from django.conf import settings

# Create your models here.
class Advertisement(models.Model):
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ads")
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, blank=True)
    PLACEMENT_CHOICES = (
        ('Homepage', 'Homepage'),
        ('Sidebar', 'Sidebar'),
    )
    placement = models.CharField(max_length=50, choices=PLACEMENT_CHOICES)
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "advertisement"

    def __str__(self):
        return self.title

