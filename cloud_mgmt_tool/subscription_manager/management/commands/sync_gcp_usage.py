from django.core.management.base import BaseCommand
from google.cloud import bigquery
from google.oauth2 import service_account
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from datetime import date
from cloud_mgmt_tool.subscription_manager.models import CloudServiceSubscription as Subscription

User = get_user_model()

class Command(BaseCommand):
    help = "Fetch GCP usage data from BigQuery and sync to Subscription table"

    def handle(self, *args, **kwargs):
        key_path = r"C:\Users\Shravni\CldMngmntTool\gcp_keys\data-fabric-453707-t8-aad6933217cf.json"
        credentials = service_account.Credentials.from_service_account_file(key_path)

        client = bigquery.Client(credentials=credentials, project=credentials.project_id)

        query = """
            SELECT
                resource.name AS resource_name,
                usage.amount AS usage_amount,
                cost,
                currency,
                export_time
            FROM
                `data-fabric-453707-t8.billing_data.gcp_billing_export_resource_v1_01FBA7_E5E623_65CFC8`
            WHERE
                export_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            ORDER BY
                export_time DESC
            LIMIT 100
        """

        self.stdout.write("Querying BigQuery for GCP usage data...")

        user, created = User.objects.get_or_create(
            email="system@gcp-sync.local",
            defaults={"username": "gcp_sync_user"},
        )
        if created:
            random_password = get_random_string(length=12)
            user.set_password(random_password)
            user.save()
            self.stdout.write(f"Created system user {user.email} for syncing.")

        try:
            query_job = client.query(query)
            results = query_job.result()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to query BigQuery: {e}"))
            return

        count = 0
        valid_record_found = False
        for row in results:
            self.stdout.write(f"Fetched row: resource_name={row.resource_name}, cost={row.cost}")
            if not row.resource_name:
                self.stdout.write(self.style.WARNING("Skipping record with empty resource_name"))
                continue

            valid_record_found = True
            obj, created = Subscription.objects.update_or_create(
                service_name=row.resource_name,
                user=user,
                cloud_provider='gcp',
                defaults={
                    "price": row.cost or 0.0,
                    "monthly_budget": 0.0,
                    "renewal_date": date.today(),
                    "status": "active",
                    "frequency": "monthly",
                    "alert_threshold": 80,
                    "usage_amount": row.usage_amount if hasattr(row, 'usage_amount') and row.usage_amount else 0.0,
                    "cost": row.cost or 0.0,
                    "usage_unit": "unknown",
                },
            )
            count += 1

        if not valid_record_found:
            self.stdout.write(
                self.style.WARNING("No valid records found. Creating a dummy subscription to confirm connection."))

            Subscription.objects.update_or_create(
                service_name="dummy-service",
                user=user,
                cloud_provider='gcp',
                defaults={
                    "price": 0.0,
                    "monthly_budget": 0.0,
                    "renewal_date": date.today(),
                    "status": "active",
                    "frequency": "monthly",
                    "alert_threshold": 80,
                    "usage_amount": 0,
                    "cost": 0,
                    "usage_unit": "units",
                },
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {count} usage records to the database!"))
