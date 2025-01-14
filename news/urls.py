# news/urls.py
from django.urls import path
from .views import ArticlesGeoJSON, WeeklyTopSummaries

urlpatterns = [
    path('news_geojson/', ArticlesGeoJSON.as_view(), name='articles_geojson'),
    path('weekly_news/', WeeklyTopSummaries.as_view(), name = 'weekly_news')
]
