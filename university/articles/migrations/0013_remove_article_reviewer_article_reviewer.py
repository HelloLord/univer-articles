# Generated by Django 5.2.3 on 2025-07-04 18:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0012_rename_reviewer_customuser_is_reviewer_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='reviewer',
        ),
        migrations.AddField(
            model_name='article',
            name='reviewer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewer', to=settings.AUTH_USER_MODEL),
        ),
    ]
