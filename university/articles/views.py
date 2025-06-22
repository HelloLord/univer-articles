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
                          ArticlePublishingSerializer, ArticleViewByPKSerializer,
                          )



"""Registration""" 'register/'
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


"""login""" 'login/'
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



"""LogOut""" 'logout/'
class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('article-list')



"""GET srlz.0 or POST Articles srlz.01""" 'articles/'
class ArticleListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Article.objects.filter(status='published')

    #Возвращает нужный сериализатор в зависимости от GET/POST запроса
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleCreateSerializer #Берет за автора, авторизованного пользователя
        return BaseArticleSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article = serializer.save()
        detail_serializer = BaseArticleSerializer(article)
        return Response(detail_serializer.data)


"""CURD ARTICLES BY PK"""
class CURDArticlesByPK(generics.RetrieveUpdateDestroyAPIView):
        queryset = Article.objects.all()
        serializer_class = ArticleViewByPKSerializer



"""All Submitted Articles srlz.0""" 'articles/publishing'
class PublishArticleView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Article.objects.filter(is_published=False)
    serializer_class = BaseArticleSerializer

"""PATCH(published) Article By PK srlz.03"""
class PublishArticleByIDView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Article.objects.all()
    serializer_class = ArticlePublishingSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={'is_published': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



"""Articles POST by Users srlz.04""" 'users/'
class UsersArticlesView(generics.ListAPIView):
    queryset = CustomUser.objects.prefetch_related('articles')
    serializer_class = UserViewSerializer



