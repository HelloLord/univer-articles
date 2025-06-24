from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.username

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

    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(CustomUser, related_name='articles')
    abstract = models.TextField()
    keywords = models.CharField(max_length=200, null=True)
    content = models.TextField(blank=True, null=True)
    submission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='submitted')
    reviewers = models.ManyToManyField(CustomUser, related_name='reviews', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title



