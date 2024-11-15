# Generated by Django 5.1.1 on 2024-09-28 10:24

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trust", "0006_trustee_details"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document_Details",
            fields=[
                ("document_id", models.AutoField(primary_key=True, serialize=False)),
                ("document_type", models.CharField(choices=[], max_length=100)),
                ("document_subtypes", models.CharField(choices=[], max_length=100)),
                ("document_name", models.CharField(max_length=255)),
                (
                    "document_attatchment",
                    models.FileField(
                        upload_to="documents/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["pdf"]
                            )
                        ],
                    ),
                ),
                ("document_description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
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
