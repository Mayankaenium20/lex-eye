# Generated by Django 5.1.1 on 2024-09-29 16:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trust", "0015_mailing_template"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Resolution",
            fields=[
                (
                    "mailing_temp_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "template_for",
                    models.CharField(
                        choices=[
                            ("notification", "Notification"),
                            ("reminder", "Reminder"),
                            ("newsletter", "Newsletter"),
                        ],
                        max_length=50,
                    ),
                ),
                ("mailing_temp_name", models.CharField(max_length=255)),
                ("mailing_temp_desc", models.TextField(blank=True, null=True)),
                (
                    "mailing_temp_attachment",
                    models.FileField(
                        blank=True, null=True, upload_to="mailing/templates"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trust_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="trust.trust_details",
                    ),
                ),
            ],
        ),
    ]