# news/utils.py
from newsapi import NewsApiClient
from transformers import pipeline
import spacy
from geopy.geocoders import Nominatim
from .models import NewsArticle
from django.utils.dateparse import parse_datetime
import time

# 초기화
newsapi = NewsApiClient(api_key='0acf8c4d915b4f04ae2477cbe171113a')
nlp = spacy.load('en_core_web_sm')
geolocator = Nominatim(user_agent="news_geo_locator")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

CATEGORIES = [
    'business',
    'entertainment',
    'general',
    'health',
    'science',
    'sports',
    'technology',
]


def extract_location(text):
    """텍스트에서 위치 엔티티 추출 및 지오코딩"""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            location = geolocator.geocode(ent.text, timeout=10)
            if location:
                return location.latitude, location.longitude
    return None, None


def compute_importance(article_text):
    """기사 텍스트로부터 요약과 중요도 계산"""
    try:
        summary_result = summarizer(article_text, max_length=150, min_length=40, do_sample=False)
        summary = summary_result[0]['summary_text']
    except Exception as e:
        print("요약 생성 중 오류 발생:", e)
        summary = ""
    importance_score = len(summary.split())
    return summary, importance_score


def fetch_and_store_top_headlines(language='en', page_size=100):
    for category in CATEGORIES:
        articles = newsapi.get_top_headlines(
            category=category,
            language=language,
            page_size=page_size,
            country='us'
        ).get('articles', [])

        for article in articles:
            url = article.get('url')
            if NewsArticle.objects.filter(url=url).exists():
                continue

            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            published_at = parse_datetime(article.get('publishedAt'))

            full_text = " ".join(filter(None, [title, description, content]))
            lat, lon = extract_location(full_text)
            summary, importance = compute_importance(full_text) if full_text else ("", 0)

            NewsArticle.objects.create(
                title=title,
                description=description,
                url=url,
                published_at=published_at,
                summary=summary,
                importance=importance,
                latitude=lat,
                longitude=lon,
                category=category
            )
