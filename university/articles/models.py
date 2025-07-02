from dataclasses import field

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation.trans_null import gettext_lazy
from pyexpat.errors import messages
from rest_framework.exceptions import ValidationError


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    reviewer = models.BooleanField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Article(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Подана на рецензирование'),
        ('under_review', 'Прошла рецензирование'),
        ('published', 'Опубликована'),
        ('rejected', 'Отклонена'),
    ]
    title = models.CharField(
        max_length=50,
        error_messages={
            'max_length': gettext_lazy('Название не может превышать 50 символов.'),
        },
        validators=[
            MinLengthValidator(5, message=gettext_lazy('Название должено содержать минимум 5 символов')),
            RegexValidator(
                regex=r'^[^!@#$%^&*()+={}\[\]|\\:;"\'<>?,~`]+$',
                message="Название содержит запрещенные символы."
            ),
        ]
    )


    authors = models.ManyToManyField(CustomUser, related_name='articles')
    abstract = models.TextField()
    keywords = models.CharField(max_length=200, null=True)
    content = models.TextField(blank=True, null=True)
    submission_date = models.DateField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='submitted')
    reviewers = models.ManyToManyField(CustomUser, related_name='reviews', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='articles/pdfs', null=True, blank=True)


class ArticleRating(models.Model):
    article = models.ForeignKey(Article,
                                on_delete=models.CASCADE,
                                related_name = 'rating')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ('article', 'user')

class UserViewHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} viewed {self.article.title}"



