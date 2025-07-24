import logging
import os.path
from datetime import timedelta
from typing import Tuple, Optional, List, Union, Any
from celery import shared_task
from django.db.models import Count, Avg
from django.utils import timezone
import PyPDF2
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from yake.core import yake
from .models import Article, UserViewHistory

logger = logging.getLogger('mailings')

"""
Показывает рекомендации пользователю
"""

def get_recommendation_articles(user):
    viewed_categories = (
        UserViewHistory.objects
        .filter(user=user)
        .values('article__category')
        .annotate(count=Count('article__category'))
        .order_by('-count')[:3]
    )

    category_ids = [item['article__category'] for item in viewed_categories]

    article_ids = (
        UserViewHistory.objects
        .filter(user=user)
        .values_list('article_id', flat=True)
    )

    recommended_articles = (
        Article.objects
        .filter(category_id__in=category_ids)
        .exclude(id__in=article_ids)
        .annotate(avg_rating=Avg('rating__rating'))
        .order_by('-avg_rating')[:10]
    )

    return recommended_articles

"""
Извлекает ключевые слова из текста
"""
class KeywordExtract:
    def __init__(self, language: str ="ru", ngrams: Tuple[int, int] = (1,2),
                 dedup_lim: float =0.9, top: int=10) -> None:
        try:
            self.extractor = yake.KeywordExtractor(
                lan=language,
                n=ngrams[1],
                dedupLim=dedup_lim,
                top=top,
                features=None
            )
        except Exception as e:
            logger.error(f"Error of initialization KeywordExtract: {str(e)}")
            raise


    def extract(self, text: str, top_n: int = 3) -> Optional[List[str]]:
        try:
            if not text or not isinstance(text, str) or not text.strip(): #Предназначено для вызова только с одним аргументом
                raise ValueError("file can't be empty")

            keywords = self.extractor.extract_keywords(text)
            filtred_keywords = [kw[0] for kw in keywords if len(kw[0]) <= 20]

            if not filtred_keywords:
                return None

            return filtred_keywords[:top_n]

        except Exception as e:
            logger.error(f"Error with extract keywords: {str(e)}")
            return None
"""
Извлекает текст из PDF файлов.
"""
class PDFProcessing:
    @staticmethod
    def extract_text(pdf_file: Union[str,Any]) -> Optional[str]:
        text = ""
        try:
            if isinstance(pdf_file,str): #в случае если это просто строка.
                return pdf_file

            pdf_reader = PyPDF2.PdfReader(pdf_file) #В случае если это файловый объект
            for page in pdf_reader.pages:
                text += page.extract_text() or ""

        except Exception as e:
            logger.error(f"Error with extract text from PDF file: {str(e)}")
            return None
        return text

    @staticmethod
    def validate_pdf_file(value: Any) -> str:
        if not value:
            return value

        file_extension = os.path.splitext(value.name)[1].lower() #Получаем формат файла
        if not value.name.lower().endswith('.pdf'):
            raise ValidationError(f'File must be format PDF'
                                  f'loaded file has: {file_extension}')
        if value.size == 0:
            raise ValidationError("File can't be empty")

        content: Optional[str] = PDFProcessing.extract_text(value)
        if content is None:
            raise serializers.ValidationError('PDF file processing error: File is corrupted')

        if len(content.strip()) < 100:
            raise serializers.ValidationError('PDF file processing error: File is corrupted')

        return content




"""
Метод служит для автоудаления отклоненных статей
"""
@shared_task
def clean_rejected_articles() -> int:
    expiration_date = timezone.now() - timedelta(days=1)
    rejected_articles = Article.objects.filter(
        status='rejected',
        updated_date__lte=expiration_date
    )

    pdf_file_paths: List[str] = []
    for article in rejected_articles:
        #проверяем на существование pdf_file в объекте article
        if hasattr(article, 'pdf_file') and article.pdf_file:
            pdf_file_paths.append(article.pdf_file.path)

    deletion_result: Tuple[int,dict] = rejected_articles.delete() #Результат выполнения метода delete
    deleted_count: int = deletion_result[0] if isinstance(deletion_result, tuple) else 0

    logger.info(f'Deleted {deleted_count} articles')

    for pdf_file_path in pdf_file_paths:
        try:
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)
                logger.debug(f"Deleted files: {pdf_file_path}, {deleted_count}")
        except Exception as e:
            logger.error(f"Error with delete files {pdf_file_path}: {e}")

    return deleted_count

