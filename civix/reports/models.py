from django.db import models
from django.conf import settings
from location.models import State, City
from news.models import News_article

class CitizenReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    article = models.ForeignKey(News_article, on_delete=models.SET_NULL, null=True, blank=True, related_name="article_reports")
    title = models.CharField(max_length=255)
    description = models.TextField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "citizen_report"

    def __str__(self):
        return self.title
