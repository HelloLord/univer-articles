# Generated by Django 5.2.3 on 2025-07-04 18:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0011_alter_article_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='reviewer',
            new_name='is_reviewer',
        ),
        migrations.RemoveField(
            model_name='article',
            name='reviewers',
        ),
        migrations.AddField(
            model_name='article',
            name='reviewer',
            field=models.ManyToManyField(blank=True, related_name='reviewer', to=settings.AUTH_USER_MODEL),
        ),
    ]
