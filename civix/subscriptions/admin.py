from django.contrib import admin
from .models import Subscription, SubscriptionTransaction

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'status', 'start_date', 'end_date')
    list_filter = ('plan_type', 'status')
    search_fields = ('user__email', 'user__username')

@admin.register(SubscriptionTransaction)
class SubscriptionTransactionAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'subscription', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('order_id', 'payment_id', 'subscription__user__email')
