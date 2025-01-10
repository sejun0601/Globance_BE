# news/urls.py
from django.urls import path
from .views import ArticlesGeoJSON

urlpatterns = [
    path('news_geojson/', ArticlesGeoJSON.as_view(), name='articles_geojson'),
]
