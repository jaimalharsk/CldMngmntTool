# gcp_usage.py
from django.contrib.auth import get_user_model
from subscription_manager.models import CloudServiceSubscription as Subscription
from google.cloud import bigquery

User = get_user_model()

def fetch_gcp_usage_and_create_subscriptions(user):
    client = bigquery.Client()

    query = """
    SELECT
      resource.name as resource_name,
      cost,
      usage_start_time,
      usage_end_time
    FROM
      `your-project.your_dataset.your_table`
    WHERE
      usage_start_time >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
    """

    query_job = client.query(query)
    results = query_job.result()

    count = 0
    for row in results:
        service_name = row.resource_name if row.resource_name else "unknown-service"
        cost = float(row.cost) if row.cost else 0.0

        obj, created = Subscription.objects.update_or_create(
            service_name=service_name,
            user=user,
            cloud_provider="gcp",
            defaults={
                "price": cost,
                "monthly_budget": 0.0,
                "renewal_date": None,
                "status": "active",
                "frequency": "monthly",
                "alert_threshold": 80,
            },
        )
        count += 1

    return count
