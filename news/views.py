# news/views.py
from django.shortcuts import render
from newsapi import NewsApiClient
from django.http import JsonResponse
from .utils import fetch_articles, articles_to_geojson

# NewsApiClient 초기화 (개인 API 키 사용)
newsapi = NewsApiClient(api_key='0acf8c4d915b4f04ae2477cbe171113a')

def news_by_category(request, category):
    # NewsAPI에서 카테고리별 헤드라인 가져오기
    top_headlines = newsapi.get_top_headlines(category=category, country='us', language='en')
    articles = top_headlines.get('articles', [])

    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, '../templates/news_list.html', context)

def news_geojson(request, category='general'):
    articles = fetch_articles(category=category)
    geojson_data = articles_to_geojson(articles)
    return JsonResponse(geojson_data)