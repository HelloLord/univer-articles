import logging
import os.path
from datetime import timedelta
from venv import logger
from celery import shared_task
from django.utils import timezone
import PyPDF2
from rest_framework import serializers
from yake.core import yake

from .models import Article

"""
Извлекает ключевые слова из текста
"""
class KeywordExtract:
    def __init__(self, language="ru", ngrams=(1,2), dedup_lim=0.9, top=10):
        try:
            self.extractor = yake.KeywordExtractor(
                lan=language,
                n=ngrams[1],
                dedupLim=dedup_lim,
                top=top,
                features=None
            )
        except Exception as e:
            raise ValueError(f"Ошибка при инициализации KeywordExtractor {str(e)}")


    def extract(self, text, top_n=3):
        try:
            if not text or not isinstance(text, str):
                raise ValueError("Файл не может быть пустым")

            keywords = self.extractor.extract_keywords(text)
            filtred_keywords = [kw[0] for kw in keywords if len(kw[0]) <= 20]

            if not filtred_keywords:
                return None

            return filtred_keywords[:top_n]

        except Exception as e:
            print(f"Ошибка при извлечении ключевых слов: {str(e)}")
            return None
"""
Извлекает текст из PDF файлов.
"""
class PDFProcessing:
    @staticmethod
    def extract_text(pdf_file):
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""

        except Exception as e:
            logging.error(f"Ошибка при извлечении текста из PDF: {str(e)}")
            return None
        return text

    @staticmethod
    def validate_pdf_file(value):
        if value:
            content = PDFProcessing.extract_text(value)
            if content is None:
                raise serializers.ValidationError('ошибка обработки PDF: '
                                                  'Файл поврежден или формат файла '
                                                  'не является PDF ')
            if len(content.strip()) < 100:
                raise serializers.ValidationError('Текст должен быть более 100 символов')
            return content
        return value



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
        #проверяем на существование pdf_file в объекте article
        if hasattr(article, 'pdf_file') and article.pdf_file:
            pdf_file_paths.append(article.pdf_file.path)
    deletion_result = rejected_articles.delete() #Результат выполнения метода delete

    deleted_count = deletion_result[0] if isinstance(deletion_result, tuple) else 0
    logger.info(f'Удалено {deleted_count} статей')

    for pdf_file_path in pdf_file_paths:
        try:
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)
                logger.info(f"файл удален: {pdf_file_path}")
        except Exception as e:
            logger.error(f"Ошибка при удалении файла {pdf_file_path}: {e}")

    return deleted_count

