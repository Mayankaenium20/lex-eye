# Generated by Django 5.1.1 on 2024-09-28 10:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trust", "0009_rename_document_subtypes_document_details_document_subtype"),
    ]

    operations = [
        migrations.RenameField(
            model_name="document_details",
            old_name="document_attatchment",
            new_name="document_attachment",
        ),
    ]
