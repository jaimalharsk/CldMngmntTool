from django.apps import AppConfig
import logging

class SubscriptionManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cloud_mgmt_tool.subscription_manager'

logger = logging.getLogger(__name__)

class SubscriptionManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cloud_mgmt_tool.subscription_manager'

    def ready(self):
        from django.contrib.auth import get_user_model
        from .models import CloudServiceSubscription
        try:
            User = get_user_model()
            sync_user = User.objects.filter(username="gcp_sync_user").first()
            if sync_user:
                deleted_count, _ = CloudServiceSubscription.objects.filter(
                    user=sync_user, is_temporary=True
                ).delete()
                logger.info(f"🧹 Deleted {deleted_count} temporary GCP subscriptions for gcp_sync_user on startup.")
        except Exception as e:
            logger.error(f"⚠️ Failed to clean temp subs on startup: {e}")
