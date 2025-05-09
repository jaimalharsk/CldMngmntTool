from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# ✅ FIX: Define User early
User = get_user_model()

class BudgetForm(forms.Form):
    provider_choices = [
        ('aws', 'AWS'),
        ('gcp', 'GCP'),
        ('azure', 'Azure'),
    ]
    monthly_budget = forms.DecimalField(
        label="Monthly Budget (₹/$)", min_value=0, decimal_places=2
    )
    cloud_provider = forms.ChoiceField(choices=provider_choices)
    service_name = forms.CharField(label="Service (optional)", required=False)
    alert_threshold = forms.IntegerField(
        label="Alert Threshold (%)",
        min_value=1, max_value=100,
        help_text="You’ll be alerted when usage exceeds this % of your budget"
    )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")  # Add more fields if needed
