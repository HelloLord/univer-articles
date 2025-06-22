from rest_framework import serializers

from .models import Category, Article, CustomUser

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


#Вложенные сериализаторы, реализуют отображения нужных полей в основных объектах
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name']

class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name']


"""VIEW ARTICLES srlz.01"""
class ArticleViewSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    authors = AuthorSerializer(many=True)
    reviewers = ReviewerSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'authors', 'title',
                  'abstract', 'keywords', 'file',
                  'submission_date', 'status', 'is_published',
                  'category', 'reviewers']


"""POST ARTICLE srlz.02"""
class ArticleCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Article
        fields = ['id', 'title',
                  'abstract', 'file',
                  'submission_date',
                  'category','category_name']

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



"""PATCH(published) Article By PK srlz.03"""
class ArticlePublishingSerializer(serializers.ModelSerializer):
    reviewers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Article
        fields = ['is_published', 'reviewers', 'author']


"""Articles posted by Users srlz.04""" 'users/'
class OnlyArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title']
class UserViewSerializer(serializers.ModelSerializer):
    articles = OnlyArticleSerializer(many=True, read_only=True)
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','username', 'first_name', 'last_name', 'articles','article_count']

    def get_article_count(self,obj):
        return obj.articles.count()



