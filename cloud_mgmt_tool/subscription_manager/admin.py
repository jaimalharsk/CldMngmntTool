from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CloudAccount,Subscription,Budget

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'company_name', 'subscription_plan', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Company Info', {'fields': ('company_name', 'subscription_plan')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Company Info', {'fields': ('company_name', 'subscription_plan')}),
    )

# Cloud Account Admin
class CloudAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'connected_on')
    search_fields = ('user__username', 'provider')
    list_filter = ('provider',)

# Budget Setting Admin
# class BudgetSettingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'provider', 'monthly_budget', 'alert_threshold', 'created_on')
#     list_filter = ('provider', 'created_on')
#     search_fields = ('user__username',)

# Subscription Admin
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_name', 'price', 'renewal_date', 'status', 'frequency')  # changed 'cost' → 'price'
    list_filter = ('status', 'frequency', 'renewal_date')
    search_fields = ('user__username', 'name')

class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'cloud_provider', 'monthly_budget', 'alert_threshold', 'created_at')
    list_filter = ('cloud_provider',)
    search_fields = ('user__username',)

# Register models with admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CloudAccount, CloudAccountAdmin)
#admin.site.register(BudgetSetting, BudgetSettingAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Budget, BudgetAdmin)
