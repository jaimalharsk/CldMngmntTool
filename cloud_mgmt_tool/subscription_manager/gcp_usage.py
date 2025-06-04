from django.contrib.auth import get_user_model
#from cloud_mgmt_tool.subscription_manager.models import CloudServiceSubscription as Subscription
from google.cloud import bigquery

User = get_user_model()

# def fetch_gcp_usage_and_create_subscriptions(user):
#     if not user or not hasattr(user, 'email'):
#         print("❌ Invalid user passed to GCP sync.")
#         return 0
#
#     # 🧹 Delete only temporary GCP subscriptions
#     temp_qs = Subscription.objects.filter(user=user, cloud_provider="gcp", is_temporary=True)
#     temp_count = temp_qs.count()
#     print(f"🧹 Found {temp_count} temporary GCP subscriptions to delete.")
#     deleted, _ = temp_qs.delete()
#     print(f"🧹 Deleted {deleted} temporary GCP subscriptions for {user.email}.")
#
#     client = bigquery.Client()
#
#     query = """
#     SELECT
#       resource.name as resource_name,
#       cost,
#       usage_start_time,
#       usage_end_time
#     FROM
#       `data-fabric-453707-t8.billing_data.gcp_billing_export_resource_v1_01FBA7_E5E623_65CFC8`
#     WHERE
#       usage_start_time >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH))
#     """
#
#     query_job = client.query(query)
#     results = query_job.result()
#
#     count = 0
#     for row in results:
#         service_name = row.resource_name or "unknown-service"
#         cost = float(row.cost or 0.0)
#
#         print(f"➕ Creating sub: {service_name} | cost: ₹{cost:.2f}")
#
#         Subscription.objects.create(
#             user=user,
#             service_name=service_name,
#             cloud_provider="gcp",
#             price=cost,
#             monthly_budget=0.0,
#             renewal_date=None,
#             status="active",
#             frequency="monthly",
#             alert_threshold=80,
#             is_temporary=True  # ✅ Ensures it's safely deletable on next sync
#         )
#
#         count += 1
#
#     print(f"✅ Synced {count} GCP subscriptions for {user.email}")
#     return count
