from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  # For AUTH_USER_MODEL reference

class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=255, blank=True, null=True)
    subscription_plan = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username

class Subscription(models.Model):
    objects = None
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    renewal_date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='active')  # active, inactive
    frequency = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
        default='monthly'  # Fixed default value
    )

    def __str__(self):
        return self.name
