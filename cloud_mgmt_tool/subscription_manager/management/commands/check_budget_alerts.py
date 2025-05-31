from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from cloud_mgmt_tool.subscription_manager.models import CloudServiceSubscription, CloudAccount, CloudAccountUsage
from django.db import models

from datetime import datetime
from decimal import Decimal



class Command(BaseCommand):
    help = 'Check if user usage exceeds budget threshold and send email alert.'

    def handle(self, *args, **kwargs):
        today = datetime.today()

        # Go through each subscription
        for sub in CloudServiceSubscription.objects.select_related('user'):
            if sub.status != 'active':
                continue

            # Match usage from CloudAccount -> CloudAccountUsage
            related_accounts = CloudAccount.objects.filter(user=sub.user, provider=sub.cloud_provider)

            usage_total = CloudAccountUsage.objects.filter(
                cloud_account__in=related_accounts,
                created_on__month=today.month,
                created_on__year=today.year
            ).aggregate(total=models.Sum('total_cost'))['total'] or 0

            threshold_value = sub.monthly_budget * (Decimal(sub.alert_threshold) / Decimal(100))

            if usage_total > threshold_value and not sub.alert_sent:
                subject = f"[Budget Alert] {sub.service_name} ({sub.cloud_provider.upper()})"
                message = (
                    f"Hi {sub.user.username},\n\n"
                    f"Your usage for {sub.service_name} has exceeded {sub.alert_threshold}% of your budget.\n"
                    f"Monthly Budget: ${sub.monthly_budget}\n"
                    f"Current Usage: ${usage_total:.2f}\n\n"
                    f"Please review your cloud service usage.\n"
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [sub.user.email],
                    fail_silently=False,
                )

                sub.alert_sent = True
                sub.save()
                self.stdout.write(f"Alert sent to {sub.user.email} for {sub.service_name}")

            elif usage_total <= threshold_value and sub.alert_sent:
                # Reset alert flag if usage goes back below threshold
                sub.alert_sent = False
                sub.save()
