from datetime import timedelta
from celery import shared_task
from django.utils import timezone
import PyPDF2
from .models import Article



"""
Метод служит для автоудаления отклоненных статей
"""
@shared_task
def clean_rejected_articles():
    expiration_date = timezone.now() - timedelta(days=1)
    deleted_count, _ = Article.objects.filter(
        status = 'rejected',
        updated_date__lte = expiration_date
    ).delete()
    return deleted_count

"""
Извлекает текст из PDF файлов.
"""
def extract_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text