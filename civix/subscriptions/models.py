from django.db import models
from django.conf import settings

# Create your models here.
class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subscription"

    def __str__(self):
        return f"{self.user} - {self.subscribed_at}"

