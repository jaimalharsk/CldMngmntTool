from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CloudServiceSubscription, CloudAccount

User = get_user_model()

class CloudServiceSubscriptionForm(forms.ModelForm):
    class Meta:
        model = CloudServiceSubscription
        fields = [
            'cloud_provider',
            'service_name',
            'price',
            'renewal_date',
            'status',
            'frequency',
            'monthly_budget',
            'alert_threshold',
        ]
        widgets = {
            'cloud_provider': forms.Select(attrs={'class': 'form-control'}),
            'service_name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'renewal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")  # Add more fields if needed

class CloudAccountForm(forms.ModelForm):
    class Meta:
        model = CloudAccount
        fields = ['provider', 'access_key', 'secret_key', 'role_arn', 'project_id', 'subscription_id', 'tenant_id']
        widgets = {
            'provider': forms.Select(attrs={'class': 'form-control'}),
            'access_key': forms.TextInput(attrs={'class': 'form-control'}),
            'secret_key': forms.TextInput(attrs={'class': 'form-control'}),
            'role_arn': forms.TextInput(attrs={'class': 'form-control'}),
            'project_id': forms.TextInput(attrs={'class': 'form-control'}),
            'subscription_id': forms.TextInput(attrs={'class': 'form-control'}),
            'tenant_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
