# Generated by Django 5.1.5 on 2025-06-04 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription_manager', '0011_alter_gcpsynclog_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloudservicesubscription',
            name='is_temporary',
            field=models.BooleanField(default=False),
        ),
    ]
