from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


# Custom User Model
class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=255, blank=True)
    subscription_plan = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username


# User Budget Record
class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount}"


# Cloud Account Connection Info
class CloudAccount(models.Model):
    PROVIDER_CHOICES = [
        ('aws', 'Amazon Web Services'),
        ('gcp', 'Google Cloud Platform'),
        ('azure', 'Microsoft Azure'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    connected_on = models.DateTimeField(auto_now_add=True)

    # AWS
    access_key = models.CharField(max_length=100, blank=True)
    secret_key = models.CharField(max_length=100, blank=True)
    role_arn = models.CharField(max_length=200, blank=True)

    # GCP
    project_id = models.CharField(max_length=100, blank=True)

    # Azure
    subscription_id = models.CharField(max_length=100, blank=True)
    tenant_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.provider.upper()}"


# Budget Settings Per Cloud Provider
class BudgetSetting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=10, choices=CloudAccount.PROVIDER_CHOICES)
    monthly_budget = models.FloatField()
    alert_threshold = models.IntegerField(default=80)  # In percent
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.provider.upper()} Budget"


# Subscriptions Tracker
class Subscription(models.Model):
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    renewal_date = models.DateField()
    status = models.CharField(max_length=20, default='active')  # active, inactive
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')

    def __str__(self):
        return f"{self.name} ({self.user.username})"
