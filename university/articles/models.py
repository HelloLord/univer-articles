from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.core.validators import RegexValidator
from django.db.models import SET_NULL
from django.utils.translation.trans_null import gettext_lazy


class CustomUser(AbstractUser):
    # Валид
    username = models.CharField(
        unique=True,
        help_text="Required: 4-30 letters, digits and @/./+/-/_ characters.",
        blank= False
    )
    # Валид
    first_name = models.CharField(
        help_text="Required: 3-10 letters.",
        blank= False
    )
    # Валид
    last_name = models.CharField(
        help_text= "Required: 3-10 letters.",
        blank= False
    )
    email = models.EmailField(
        unique=True,
        blank=False
    )
    phone = models.CharField(
        unique=True,
        blank=False,
    )
    password = models.CharField(
        help_text='Required: At least 8 characters '
                  'including letters and numbers.',
        blank=False

    )
    birth_date = models.DateField(
        blank=True,
        null=True)

    is_reviewer = models.BooleanField(default=False)


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
    abstract = models.TextField(null=False)
    keywords = models.CharField(max_length=200, null=True)
    content = models.TextField(blank=False, null=True)
    submission_date = models.DateField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='submitted')
    reviewer = models.ForeignKey(CustomUser, related_name='reviewer', blank=True, on_delete=SET_NULL, null=True)
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



