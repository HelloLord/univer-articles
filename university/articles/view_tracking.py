from django.db.models import Count
from .models import UserViewHistory

#Трекинг колличества просмотров статьи
def track_article_view(user,article):
    if user.is_authenticated:
        UserViewHistory.objects.create(user=user, article=article)

#10 наиболее просматриваемых статей
def most_viewed_articles(limit=10):
    return UserViewHistory.objects.values('article').annotate(
        view_count=Count('article')
    ).order_by('-view_count')[:limit]

