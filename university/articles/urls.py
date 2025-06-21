from django.shortcuts import redirect
from django.urls import path


from .views import (ArticleListCreateView, ArticleRetrieveUpdateDestroyView,
                    RegisterView, UsersArticlesView,
                    ArticlesSubmitted, LogoutView, LoginAPIView)


def home_redirect(request):
    return redirect('articles/')

urlpatterns = [
    path('', home_redirect,),
    #register user, login, logout
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name ='logout'),
    path('login/', LoginAPIView.as_view(), name='login'),
    #create, view, view detail
    path('articles/', ArticleListCreateView.as_view(), name='article-list'),
    path('articles/<int:pk>', ArticleRetrieveUpdateDestroyView.as_view(), name='article-detail'),
    #users with article
    path('users/', UsersArticlesView.as_view(), name='users-list'),
    #is published articles
    path('articles/publishing', ArticlesSubmitted.as_view(), name='publishing-articles'),
]