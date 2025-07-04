from django.db.models import Avg
from rest_framework import serializers

from .models import Category, Article, CustomUser, ArticleRating, UserViewHistory
from .utils import KeywordExtract, extract_pdf

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
            raise serializers.ValidationError("Username is required")
        if not value.isalnum():
            raise serializers.ValidationError("Username must contain only letters and numbers.")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with that username already exists.")
        return value

    def validate_email(self,value):
        if not value:
            raise serializers.ValidationError("Email is required")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_phone(self,value):
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone already exists.")
        return value

    def create(self, validated_data):
        print("validated data", validated_data)
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
            print("User created:", user.username, user.phone)
            return user
        except Exception as e:
            raise serializers.ValidationError('Error creating user: '+ str(e))

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
        if value:
            try:
                content = extract_pdf(value)
                if len(content.strip()) < 100:
                    raise serializers.ValidationError('Текст должен быть более 100 символов')

            except Exception as e:
                raise serializers.ValidationError(
                    f"Ошибка обработки PDF: {str(e)}"
                )
        return value

        #Проверка на загрузку статьи в PDF формате, либо в формате текста
    def validate(self, data):
        if not data.get('content') and not data.get('pdf_file'):
            raise serializers.ValidationError('Должен быть либо текст статьи либо PDF-файл')

        if data.get('content') and data.get('pdf_file'):
            raise serializers.ValidationError('Предоставьте что-то одно, '
                                               'либо текст статьи либо PDF файл,'
                                             'но не оба варианта')
        if data.get('content') and len(data['content'].strip()) < 100:
            raise serializers.ValidationError(
                'Текст статьи должен содержать не менее 100 символов'
            )

        return data

    def create(self,validated_data):
        pdf_file = validated_data.pop('pdf_file', None)

        if pdf_file:
            validated_data['content'] = extract_pdf(pdf_file)

        content = validated_data.get('content', '')
        if len(content.strip()) <100:
            raise serializers.ValidationError(
                'Текст должен содержать не менее 100 символов'
            )

        #Берет за автора, Текущего авторизированного пользователя.
        current_user = self.context['request'].user
        category = validated_data.pop('category')

        content = validated_data.get('content','')
        keywords = KeywordExtract().extract(content) #извлекаем ключевые слова из поля content
        article = Article.objects.create(**validated_data)

        if hasattr(article,'keywords'):
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
            raise serializers.ValidationError("Вы уже оценили эту статью.")
        rating = data.get('rating')
        if rating < 1 or rating > 5:
            raise serializers.ValidationError('Оценка должна быть от 1 до 5')
        return data


