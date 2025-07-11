from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import logout,authenticate,login
from django.views import View
from rest_framework.views import APIView
from rest_framework import filters
from django_filters import rest_framework as django_filters

from .view_tracking import track_article_view

from .utils import clean_rejected_articles, get_recommendation_articles

from .self_permissions import IsReviewerOrAdmin, IsStuffOrAdmin

from .pagination import LargeSetPagination,SmallSetPagination

from .models import Article, CustomUser

from .serializers import (BaseArticleSerializer, CustomUserSerializer,
                          UserViewSerializer, ArticleCreateSerializer,
                          ArticleViewByPKSerializer, ArticleReviewSerializer, ArticlePublishSerializer,
                          ArticleRatingSerializer
                          )

"""register/"""
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()
        login(request, user)

        return redirect('article-list')


"""login/"""
class LoginAPIView(APIView):

    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('article-list')
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


"""logout/"""
class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('article-list')


"""
articles/rec
Выводит список рекомендаций, для авторизированного пользователя.
"""
class ArticleRecommendationView(generics.ListAPIView):
    serializer_class = BaseArticleSerializer

    def get_queryset(self):
        user = self.request.user
        return get_recommendation_articles(user)



"""
articles/
Выводит список опубликованных статей + фильтрация
"""

class ArticleListView(generics.ListAPIView):
    serializer_class = BaseArticleSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SmallSetPagination

    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['title', 'category__name']
    search_fields = ['abstract', 'content', 'keywords']
    ordering_fields = ['title', 'updated_date', 'views']
    ordering = ['-updated_date']

    def get_queryset(self):
        return Article.objects.filter(
            is_published=True,
            status='published'
        ).select_related('category')

"""
articles/<int:pk>
Выводит конкретную статью по ID
"""
class ArticleDetailView(generics.RetrieveAPIView):
    serializer_class = BaseArticleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Article.objects.filter(status='published')

    def get(self, request, *args, **kwargs):
        response = super().get(request,*args,**kwargs)
        article = self.get_object()
        track_article_view(request.user, article)

        return response


"""
articles/<int:pk>/ratin
Оценка статьи по ID
(только для авторизированных пользователей)
"""
class ArticleRatingView(generics.CreateAPIView):
    serializer_class = ArticleRatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        article = generics.get_object_or_404(Article, pk=self.kwargs.get('pk'))
        serializer.save(user=self.request.user, article=article)

    def post(self, request, *args, **kwargs):
        return self.create(request,*args,**kwargs)

"""
articles/create
Служит для создания новой статьи
Возможность загрузки сататьи в формете PDF 
(только для авторизированных пользователей)
"""
class ArticleCreateView(generics.CreateAPIView):
    serializer_class = ArticleCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



"""
articles/review
Выводит список статей которые подны на рецензию
(только для рецензиатов и админа)
"""
class ReviewArticleView(generics.ListAPIView):
    permission_classes = [IsReviewerOrAdmin]
    serializer_class = BaseArticleSerializer
    pagination_class = SmallSetPagination

    def get_queryset(self):
        return Article.objects.filter(status='submitted').order_by('-updated_date')


"""
articles/review<int:pk>
Служит для рецензии статьи
(только для рецензиатов и админа)
"""
class ReviewArticleByIDView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsReviewerOrAdmin]
    serializer_class = ArticleReviewSerializer

    def get_queryset(self):
        return Article.objects.filter(status='submitted')


"""
articles/rejected
Выводит список отклоненных статей после рецензирования
(только для рецензиатов и админа)
"""

class RejectArticlesList(generics.ListAPIView):
    permission_classes = [IsReviewerOrAdmin]
    serializer_class = BaseArticleSerializer
    pagination_class = SmallSetPagination

    def get_queryset(self):
        # удаляет отклоненную статью, через 1 день
        clean_rejected_articles()
        return Article.objects.filter(status='rejected').order_by('-updated_date')


"""
articles/publishing
Выводит список статей прошедших рецензирование
(Для админа или модераторов)
"""
class PublishArticleView(generics.ListAPIView):
    permission_classes = [IsStuffOrAdmin]
    serializer_class = BaseArticleSerializer
    pagination_class = SmallSetPagination

    def get_queryset(self):
        return Article.objects.filter(status='under_review').order_by('-updated_date')


"""
articles/publishing/<int:pk>
Выводит статью для публикации, которая прошла рецензирование  
(Для админа или модераторов)
"""
class PublishArticleIDView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsStuffOrAdmin]
    queryset = Article.objects.filter(status='under_review')
    serializer_class = ArticlePublishSerializer


"""
articles/admin/<int:pk>
Выводит одну статью для всех операий.
(Для админа или модераторов)
"""
class CURDArticlesByPK(generics.RetrieveUpdateDestroyAPIView):
        permission_classes = [IsStuffOrAdmin]
        queryset = Article.objects.all()
        serializer_class = ArticleViewByPKSerializer


"""
articles/users
Выводит список всех пользователей, колличество их статей.
(Для админа или модераторов)
"""
class UsersArticlesView(generics.ListAPIView):
    pagination_class = LargeSetPagination
    permission_classes = [IsStuffOrAdmin]
    queryset = CustomUser.objects.prefetch_related('articles')
    serializer_class = UserViewSerializer




