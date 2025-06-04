from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cloud_mgmt_tool.subscription_manager.gcp_usage import fetch_gcp_usage_and_create_subscriptions
from django.contrib.auth.hashers import make_password
User = get_user_model()

class Command(BaseCommand):
    help = "Sync GCP usage data from BigQuery into CloudServiceSubscription"

    def handle(self, *args, **options):
        user_email = "system@gcp-sync.local"
        user, created = User.objects.get_or_create(
            email=user_email,
            defaults={"username": user_email, "password": make_password("gcp-sync-pass123")},
        )
        if created:
            self.stdout.write(f"Created system user {user_email} for syncing.")

        # ✅ Step 1: Remove old temporary GCP subscriptions for this user
        from cloud_mgmt_tool.subscription_manager.models import CloudServiceSubscription
        deleted, _ = CloudServiceSubscription.objects.filter(user=user, is_temporary=True).delete()
        self.stdout.write(f"Deleted {deleted} old temporary GCP subscriptions.")

        # ✅ Step 2: Run the sync function
        count = fetch_gcp_usage_and_create_subscriptions(user)
        self.stdout.write(f"GCP usage sync complete. {count} subscriptions processed.")
