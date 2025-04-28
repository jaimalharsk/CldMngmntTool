from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Subscription
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'renewal_date', 'status', 'frequency')

admin.site.register(Subscription, SubscriptionAdmin)


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('company_name', 'subscription_plan')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
