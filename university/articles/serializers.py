from time import timezone

from django.db.models import Avg
from rest_framework import serializers

from .models import Category, Article, CustomUser, ArticleRating

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
    reviewers = ReviewerSerializer(many=True)

    average_rating = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    can_rate = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'authors', 'abstract', 'keywords', 'content',
            'submission_date','updated_date', 'status', 'reviewers', 'category', 'is_published',
            'average_rating', 'user_rating', 'can_rate'

        ]

        read_only_fields = ['submission_date', 'status', 'can_rate']

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



'''Реализует создание статьи с учетом текущего авторизированного пользователя'''
class ArticleCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Article
        fields = ['id', 'title',
                  'abstract', 'content',
                  'category']

    def create(self,validated_data):
        #Берет за автора, Текущего авторизированного пользователя.
        current_user = self.context['request'].user
        reviewers = validated_data.pop('reviewers', [])
        category = validated_data.pop('category')
        article = Article.objects.create(**validated_data)
        article.authors.add(current_user)
        article.reviewers.set(reviewers)
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
    reviewers = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(reviewer = True),
        many = True
    )
    STATUS_CHOICES = [
        ('under_review', 'Прошла рецензирование'),
        ('rejected', 'Отклонена'),
    ]
    status = serializers.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['is_published']

    def update(self, instance, validated_data):
        reviewers = validated_data.pop('reviewers', [])
        instance = super().update(instance, validated_data)
        instance.reviewers.clear()
        instance.reviewers.add(*reviewers)
        instance.save()
        return instance



'''Добавляет статью is_published=True'''
'''Реализует публикацию статьи, которая прошла рецензирование'''
'''/articles/publish/<int:pk>'''
class ArticlePublishSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True,read_only=True)
    reviewers = ReviewerSerializer(many=True,read_only=True)
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = [
            'id', 'title', 'abstract', 'content', 'keywords',
            'submission_date', 'status', 'category', 'authors', 'reviewers',
            'updated_date'
        ]

    def update(self, instance, validated_data):
        instance.is_published = validated_data.get('is_published', False)
        instance.status = 'published'
        instance.save()
        return instance




"""CURD ARTICLES BY PK srlz.04"""
'''articles/<int:pk>'''
class ArticleViewByPKSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


"""Articles posted by Users srlz.04"""
'''users/'''
'''Показывает зарегистрированных пользователей '''
class UserViewSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','username', 'first_name', 'last_name', 'articles','article_count','reviewer']

    def get_article_count(self,obj):
        return obj.articles.count()





