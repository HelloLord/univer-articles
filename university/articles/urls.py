from django.shortcuts import redirect
from django.urls import path


from .views import (ArticleListCreateView,
                    RegisterView, UsersArticlesView,
                    LogoutView, LoginAPIView,
                    CURDArticlesByPK, ReviewArticleByIDView,
                    ReviewArticleView, PublishArticleView, PublishArticleIDView)


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
    path('articles/<int:pk>',CURDArticlesByPK.as_view(),),
    #users with article
    path('users/', UsersArticlesView.as_view(), name='users-list'),
    # Review articles
    path('articles/review', ReviewArticleView.as_view(),
         name='review-articles'),
    path('articles/review/<int:pk>', ReviewArticleByIDView.as_view(),
         name = 'review-articles-pk'),

    path('articles/publish', PublishArticleView.as_view(), name='publish-article'),
    path('articles/publish/<int:pk>', PublishArticleIDView.as_view(), name = 'publish-article-pk')
]