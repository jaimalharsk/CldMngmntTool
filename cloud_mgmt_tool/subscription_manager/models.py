from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# --- Custom User Model ---
class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=255, blank=True, default="")
    subscription_plan = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return self.username


# --- Unified Subscription + Budget Model ---
class CloudServiceSubscription(models.Model):
    CLOUD_PROVIDERS = [
        ('aws', 'Amazon Web Services'),
        ('gcp', 'Google Cloud Platform'),
        ('azure', 'Microsoft Azure'),
        ('other', 'Other'),
        ('all', 'All Providers'),  # Optional aggregate budget
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancelled', 'Cancelled'),
    ]

    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cloud_provider = models.CharField(
        max_length=10,
        choices=CLOUD_PROVIDERS,
        default='all',
        help_text="Choose the cloud provider."
    )
    service_name = models.CharField(max_length=100, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    renewal_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')

    monthly_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Monthly budget limit in USD."
    )
    alert_threshold = models.PositiveIntegerField(
        default=80,
        help_text="Threshold percentage at which to alert the user."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    # inside CloudServiceSubscription model
    alert_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.service_name} ({self.cloud_provider.upper()}) - {self.user.username}"


# --- Cloud Account Info ---
class CloudAccount(models.Model):
    PROVIDER_CHOICES = [
        ('aws', 'Amazon Web Services'),
        ('gcp', 'Google Cloud Platform'),
        ('azure', 'Microsoft Azure'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, default='aws')
    connected_on = models.DateTimeField(auto_now_add=True)

    # AWS
    access_key = models.CharField(max_length=255, default="", blank=True)
    secret_key = models.CharField(max_length=100, default="", blank=True)
    role_arn = models.CharField(max_length=255, default="", blank=True)

    # GCP
    project_id = models.CharField(max_length=255, default="", blank=True)

    # Azure
    subscription_id = models.CharField(max_length=100, default="", blank=True)
    tenant_id = models.CharField(max_length=100, default="", blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.provider.upper()}"


# --- Cloud Usage Tracker ---
class CloudAccountUsage(models.Model):
    cloud_account = models.ForeignKey(CloudAccount, on_delete=models.CASCADE)
    total_cost = models.FloatField(default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cloud_account} - ${self.total_cost:.2f} on {self.created_on.date()}"
