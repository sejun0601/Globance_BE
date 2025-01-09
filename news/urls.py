# news/urls.py
from django.urls import path
from .views import news_by_category, news_geojson

urlpatterns = [
    path('<str:category>/', news_by_category, name='news_by_category'),
    path('geojson/<str:category>/', news_geojson, name='news_geojson'),
]
