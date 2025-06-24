from audioop import reverse

from django.http import HttpResponseBase, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.auth import logout,authenticate,login
from django.views import View
from rest_framework.views import APIView

from .models import Article, CustomUser
from .serializers import (BaseArticleSerializer, CustomUserSerializer,
                          UserViewSerializer, ArticleCreateSerializer,
                          ArticleViewByPKSerializer, ArticleReviewSerializer, ArticlePublishSerializer)

'''register/'''
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

'''login/'''
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

'''logout/'''
class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('article-list')





'''articles/ '''
'''Выводит список статей, которые уже прошли рецензию и опубликованы '''
class ArticleListView(generics.ListAPIView):
    serializer_class = BaseArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Article.objects.filter(status = 'published')

'''articles/create'''
'''Публиковать могут только авторизированные пользователи'''
class ArticleCreateView(generics.CreateAPIView):
    serializer_class = ArticleCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


'''articles/review'''
'''Выводит список статей, которые поданы на рецензирование '''
class ReviewArticleView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Article.objects.filter(status='submitted')
    serializer_class = BaseArticleSerializer


''''articles/review<int:pk>'''
'''Рецензирование конкретной статьи по ID '''
class ReviewArticleByIDView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ArticleReviewSerializer

    def get_queryset(self):
        return Article.objects.filter(status='submitted')

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = generics.get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_update(self, serializer):
        serializer.save()
        return redirect('review-articles')

'''articles/rejected'''
'''Выводит список отклоненных статей'''
class RejectArticlesList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Article.objects.filter(status='rejected')
    serializer_class = BaseArticleSerializer


'''articles/publishing '''
'''Выводит список статей готовых к публикации'''
class PublishArticleView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Article.objects.filter(status='under_review')
    serializer_class = BaseArticleSerializer

'''articles/publishing/<int:pk>'''
'''Публикация конкретной статьи по ID'''
class PublishArticleIDView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Article.objects.filter(status='under_review')
    serializer_class = ArticlePublishSerializer


'''articles/<int:pk>'''
class CURDArticlesByPK(generics.RetrieveUpdateDestroyAPIView):
        permission_classes = [IsAuthenticatedOrReadOnly]
        queryset = Article.objects.all()
        serializer_class = ArticleViewByPKSerializer

"""Articles POST by Users srlz.04"""
'''users/'''
class UsersArticlesView(generics.ListAPIView):
    queryset = CustomUser.objects.prefetch_related('articles')
    serializer_class = UserViewSerializer



