# Generated by Django 5.2.3 on 2025-06-24 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_alter_article_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='updated_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('submitted', 'Подана на рецензирование'), ('under_review', 'Прошла рецензирование'), ('published', 'Опубликована'), ('rejected', 'Отклонена')], default='submitted', max_length=20),
        ),
    ]
