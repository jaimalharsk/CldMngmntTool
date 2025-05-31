from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CloudAccount, CloudServiceSubscription, CloudAccountUsage

# --- Custom User Admin ---
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'company_name', 'subscription_plan', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Company Info', {'fields': ('company_name', 'subscription_plan')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Company Info', {'fields': ('company_name', 'subscription_plan')}),
    )

# --- Cloud Account Admin ---
class CloudAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'connected_on')
    search_fields = ('user__username', 'provider')
    list_filter = ('provider',)

# --- Cloud Service Subscription Admin (Unified Model) ---
class CloudServiceSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'cloud_provider', 'service_name', 'price', 'renewal_date',
        'status', 'frequency', 'monthly_budget', 'alert_threshold', 'created_at'
    )
    list_filter = ('cloud_provider', 'status', 'frequency', 'created_at')
    search_fields = ('user__username', 'service_name')

# --- Cloud Usage Admin ---
class CloudAccountUsageAdmin(admin.ModelAdmin):
    list_display = ('cloud_account', 'total_cost', 'created_on')
    list_filter = ('cloud_account__provider', 'created_on')
    search_fields = ('cloud_account__user__username',)

# --- Register Models ---
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CloudAccount, CloudAccountAdmin)
admin.site.register(CloudServiceSubscription, CloudServiceSubscriptionAdmin)
admin.site.register(CloudAccountUsage, CloudAccountUsageAdmin)
