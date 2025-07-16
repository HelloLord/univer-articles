import re

from django.db.models import Avg
from django.db.models.query_utils import logger
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, Article, CustomUser, ArticleRating, UserViewHistory
from .utils import KeywordExtract, PDFProcessing
from ..university.settings import STATIC_URL

"""CREATE USER"""
class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username','first_name','last_name','email', 'password', 'phone', 'avatar', 'birth_date')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'write_only': True},
        }
    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("field username is required")

        if value[0].isdigit() or value.isdigit() or value[0] in '@/./+/-/_':
            raise serializers.ValidationError(
                "Username can't start with '@/./+/-/_', and cannot be entirely numeric"
            )

        if len(value) < 4 or len(value) > 30:
            raise serializers.ValidationError("Username name must be least 4 characters long or cannot exceed 30 characters")

        if not re.match(r'[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                "Username can only contain letters, digits and @/./+/-/_ characters")

        if CustomUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(f"Username '{value}' is already taken")

        reserved_names = {'admin', 'root', 'me', 'superuser', 'reviewer'}
        if value.lower() in reserved_names:
            raise serializers.ValidationError(f"Username '{value}' is reserved")
        return value

    def validate_first_name(self,value):
        value = value.capitalize()
        if not value:
            raise serializers.ValidationError('field is required')

        if len(value) < 3 or len(value) > 15:
            raise serializers.ValidationError("first name must be least 3 characters long or cannot exceed 15 characters")

        if not re.match(r'^[A-Za-z]+$', value):
            raise serializers.ValidationError('first name must contains only english letters')




    def validate_email(self,value):
        if not value:
            raise serializers.ValidationError("field email is required")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(f"account with email {value} already exists.")
        return value

    def validate_phone(self,value):
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError(f"account with phone {value} already exists.")
        return value

    def create(self, validated_data):
        try:
            user = CustomUser.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                phone=validated_data.get('phone', ''),
                birth_date=validated_data.get('birth_date')
            )
            logger.info(f"user create: {user.username}")
            return user
        except Exception as e:
            logger.error(f"error with register user: {str(e)}")
            raise serializers.ValidationError('error with register: '+ str(e))

"""Вложенные сериализаторы, реализуют отображения нужных полей в основных объектах"""
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name']

class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name']


class OnlyArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title']



"""Базовый сериализатор, реализует поля Article и поля вложенных объектов сериализаторов"""
'''articles/' | 'articles/review | /articles/publish'''
class BaseArticleSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    reviewer = ReviewerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    average_rating = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    can_rate = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'authors', 'abstract', 'keywords', 'content','submission_date',
            'submission_date','updated_date', 'status', 'reviewer', 'category', 'is_published',
            'average_rating', 'user_rating', 'can_rate', 'views'

        ]

        read_only_fields = [ 'status', 'can_rate']

    def get_average_rating(self, obj):
        avg = obj.rating.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else None

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.rating.filter(user=request.user).first()
            return rating.rating if rating else None
        return None

    def get_can_rate(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and not obj.rating.filter(user=request.user).exists())

    #метод подсчета просмотров статьи
    def get_views(self,obj):
        return UserViewHistory.objects.filter(article=obj).count()



'''articles/create'''
'''Реализует создание статьи с учетом текущего авторизированного пользователя'''
class ArticleCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Article
        fields = ['id', 'title',
                  'abstract', 'content',
                  'category','pdf_file']

    def validate_pdf_file(self,value):
        return PDFProcessing.validate_pdf_file(value)

        #Проверка на загрузку статьи в PDF формате, либо в формате текста
    def validate(self, data):
        content = data.get('content')
        pdf_file = data.get('pdf_file')

        if not content and not pdf_file:
            raise serializers.ValidationError('Must be text or PDF file.')

        if content and pdf_file:
            raise serializers.ValidationError('Please, provide one of these'
                                              'enter the text of the article or PDF file'
                                              'but not both')
        if content and len(content.strip()) < 100:
            raise serializers.ValidationError(
                'Text of article must contains, not less then 100 symbols'
            )

        return data

    def create(self,validated_data):
        pdf_file = validated_data.pop('pdf_file', None)
        if pdf_file:
            validated_data['content'] = PDFProcessing.extract_text(pdf_file)

        current_user = self.context['request'].user
        category = validated_data.pop('category')

        content = validated_data.get('content','')
        if not content:
            raise ValidationError("field content can't be empty")

        keywords = KeywordExtract().extract(content) #извлекаем ключевые слова из поля content
        article = Article.objects.create(**validated_data)

        #Возворащаем пустой список если список keywords пуст
        if hasattr(article,'keywords'):
            if keywords is None:
                keywords = []
            article.keywords = ', '.join(keywords)

        article.authors.add(current_user)
        article.category = category
        article.save()
        return article



''''articles/review<int:pk>'''
'''Реализует рецензирование статьи'''
'''рецензентом может быть как авторизированный пользователь'''
'''так и возможность выбрать самому из списка'''
'''реализована возможность отмены статьи'''
class ArticleReviewSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False
    )
    STATUS_CHOICES = [
        ('under_review', 'Прошла рецензирование'),
        ('rejected', 'Отклонена'),
    ]
    status = serializers.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['is_published','pdf_file','reviewer']

    def update(self, instance, validated_data):
        current_user = self.context['request'].user
        instance = super().update(instance, validated_data)
        instance.reviewer = current_user
        instance.save()
        return instance



'''Реализует публикацию статьи, которая прошла рецензирование'''
'''/articles/publish/<int:pk>'''
class ArticlePublishSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True,read_only=True)
    reviewer = ReviewerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    STATUS_CHOICES = [
        ('published', 'Опубликовать'),
        ('rejected', 'Отклонить')]

    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = [
            'id', 'title', 'abstract', 'content', 'keywords',
            'submission_date', 'category', 'authors', 'reviewers',
            'updated_date', 'is_published','pdf_file'
        ]

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            instance.status = validated_data['status']
            instance.is_published = True
            instance.status = 'published'
        instance.save()
        return instance


"""CURD ARTICLES BY PK"""
'''articles/<int:pk>'''
class ArticleViewByPKSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


"""
articles/users
"""
class UserViewSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','username', 'first_name', 'last_name', 'articles','article_count','reviewer']

    def get_article_count(self,obj):
        return obj.articles.count()


"""
articles/ratings
Оценка статьи
"""
class ArticleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRating
        fields = ['id', 'user', 'rating']
        read_only_fields = ['user']

    def validate(self,data):
        user = self.context['request'].user
        article = data.get('article')
        if ArticleRating.objects.filter(user=user, article=article).exists():
            raise serializers.ValidationError("You already rate this article")
        rating = data.get('rating')
        if rating < 1 or rating > 5:
            raise serializers.ValidationError('Rating must be from 1 to 5')
        return data


