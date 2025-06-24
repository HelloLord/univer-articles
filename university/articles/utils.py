from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from .models import Article


@shared_task
def clean_rejected_articles():
    expiration_date = timezone.now() - timedelta(days=5)
    deleted_count, _ = Article.objects.filter(
        status = 'rejected',
        updated_date = expiration_date
    ).delete()
    return deleted_count
