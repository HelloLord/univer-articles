from django.shortcuts import redirect
from django.urls import path


from .views import (ArticleListCreateView,
                    RegisterView, UsersArticlesView,
                    PublishArticleView, LogoutView, LoginAPIView,
                    PublishArticleByIDView)


def home_redirect(request):
    return redirect('articles/')

urlpatterns = [
    path('', home_redirect,),
    #register user, login, logout
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name ='logout'),
    path('login/', LoginAPIView.as_view(), name='login'),
    #create, view, view detail published
    path('articles/', ArticleListCreateView.as_view(), name='article-list'),
    #users with article
    path('users/', UsersArticlesView.as_view(), name='users-list'),
    #is published articles
    path('articles/publishing', PublishArticleView.as_view(),
         name='publishing-articles'),

    path('articles/publishing/<int:pk>', PublishArticleByIDView.as_view(),
         name = 'publishing-articles-pk')
]