from django.shortcuts import redirect
from django.urls import path


from .views import (ArticleCreateView,
                    RegisterView, UsersArticlesView,
                    LogoutView, LoginAPIView,
                    CURDArticlesByPK, ReviewArticleByIDView,
                    ReviewArticleView, PublishArticleView,
                    PublishArticleIDView, ArticleListView,
                    RejectArticlesList, ArticleDetailView, ArticleRatingView,
                    ArticleRecommendationView, UserViewHistory)


def home_redirect(request):
    return redirect('articles/')

urlpatterns = [
    path('', home_redirect,),
    #register user, login, logout
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name ='logout'),
    path('login', LoginAPIView.as_view(), name='login'),

    #create, view, view detail published
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<int:pk>', ArticleDetailView.as_view(), name='article-pk'),
    path('articles/<int:pk>/rating', ArticleRatingView.as_view(), name ='article-rate'),
    path('articles/create', ArticleCreateView.as_view(), name='article-create'),

    #curd operations for admin
    path('articles/admin/<int:pk>', CURDArticlesByPK.as_view(), name='article-curd'),

    #review article
    path('articles/review', ReviewArticleView.as_view(),
         name='review-articles'),
    path('articles/review/<int:pk>', ReviewArticleByIDView.as_view(),
         name = 'review-articles-pk'),

    # publishing articles
    path('articles/publishing', PublishArticleView.as_view(), name='publish-article'),
    path('articles/publishing/<int:pk>', PublishArticleIDView.as_view(), name='publish-article-pk'),

    #list of rejected articles
    path('articles/rejected', RejectArticlesList.as_view(), name= 'rejected-articles'),

    #list of recommendations for self.user
    path('articles/rec', ArticleRecommendationView.as_view(), name= 'articles-recommendations'),

    # users with article
    path('users', UsersArticlesView.as_view(), name='users-list'),




    #"""TEST"""
    path('article/view/his', UserViewHistory.as_view(),)
    ]


