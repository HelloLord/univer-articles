from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import logout,authenticate,login
from django.views import View
from rest_framework.views import APIView

from .models import Article, CustomUser
from .serializers import (ArticleViewSerializer, CustomUserSerializer,
                          UserViewSerializer, ArticleCreateSerializer,
                          ArticleDetailSerializer)

"""Registration"""
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

"""login"""
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

"""LogOut"""
class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('article-list')

"""GET or POST Articles"""
class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleCreateSerializer #Берет за автора, авторизованного пользователя
        return ArticleViewSerializer

    #Передаем в запрос в нужный сериализатор
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_vaild(raise_exeption=True)
        article = serializer.save
        detail_serializer = ArticleViewSerializer(article)
        return Response(detail_serializer.data)

"""CURD Articles by PK"""
class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer


"""Articles posted by Users"""
class UsersArticlesView(generics.ListAPIView):
    queryset = CustomUser.objects.prefetch_related('articles')
    serializer_class = UserViewSerializer


"""Submitted Articles"""
class ArticlesSubmitted(generics.ListAPIView):
    queryset = Article.objects.filter(is_published=False)
    serializer_class = ArticleViewSerializer


