from celery import shared_task
from django.contrib.auth import get_user_model
from cloud_mgmt_tool.subscription_manager.gcp_usage import fetch_gcp_usage_and_create_subscriptions

User = get_user_model()

@shared_task
def sync_all_gcp_users_usage():
    from cloud_mgmt_tool.subscription_manager.models import CloudAccount
    gcp_accounts = CloudAccount.objects.filter(provider='gcp')

    total = 0
    for acc in gcp_accounts:
        if acc.user and acc.project_id:
            count = fetch_gcp_usage_and_create_subscriptions(acc.user, acc.project_id)
            total += count
    return f"Synced {total} records for all GCP users"
