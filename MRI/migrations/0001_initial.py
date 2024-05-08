# Generated by Django 5.0.6 on 2024-05-07 21:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MRI",
            fields=[
                ("user_mri_id", models.AutoField(primary_key=True, serialize=False)),
                ("image", models.URLField()),
                ("result", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "patient_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
