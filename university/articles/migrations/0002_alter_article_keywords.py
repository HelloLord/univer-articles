# Generated by Django 5.2.3 on 2025-06-22 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='keywords',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
