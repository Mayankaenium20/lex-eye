# Generated by Django 5.1.1 on 2024-09-28 18:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trust", "0012_alter_document_details_created_by"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mailing_template",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="mailing_template",
            name="trust_id",
        ),
        migrations.DeleteModel(
            name="Document_Details",
        ),
        migrations.DeleteModel(
            name="Mailing_Template",
        ),
    ]
