import logging
import os.path
from datetime import timedelta
from venv import logger

from celery import shared_task
from django.utils import timezone
import PyPDF2
from yake.core import yake

from .models import Article

"""
Извлекает ключевые слова из текста
"""
class KeywordExtract:
    def __init__(self, language="ru", ngrams=(1,2), dedup_lim=0.9, top=10):
        self.extractor = yake.KeywordExtractor(
            lan=language,
            n=ngrams[1],
            dedupLim=dedup_lim,
            top=top,
            features=None
        )

    def extract(self, text, top_n=3):
        keywords = self.extractor.extract_keywords(text)
        return [kw[0] for kw in keywords[:top_n]]


"""
Метод служит для автоудаления отклоненных статей
"""
@shared_task
def clean_rejected_articles():
    expiration_date = timezone.now() - timedelta(days=1)
    rejected_articles = Article.objects.filter(
        status='rejected',
        updated_date__lte=expiration_date
    )

    pdf_file_paths = []
    for article in rejected_articles:
        #проверяем на существование pdf_file
        if hasattr(article, 'pdf_file') and article.pdf_file:
            pdf_file_paths.append(article.pdf_file.path)
    deletion_result = rejected_articles.delete()

    deleted_count = deletion_result[0] if isinstance(deletion_result, tuple) else 0

    for pdf_file_path in pdf_file_paths:
        try:
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)
                logger.info(f"Удален файл: {pdf_file_path}")
        except Exception as e:
            logger.error(f"Ошибка при удалении файла {pdf_file_path}: {e}")

    return deleted_count

"""
Извлекает текст из PDF файлов.
"""
def extract_pdf(pdf_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

    except Exception as e:
        logging.error(f"Ошибка при извлечении текста из PDF: {e}")
        return None
    return text

