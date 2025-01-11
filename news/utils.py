# news/utils.py
from newsapi import NewsApiClient
from transformers import pipeline
from .models import NewsArticle
from django.utils.dateparse import parse_datetime
from django.conf import settings
import time
import torch
print("CUDA Available:", torch.cuda.is_available())

from geoparser import Geoparser

# Geoparser 초기화 (모델 로드 등)
geo = Geoparser()

# 초기화
newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
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
    docs = geo.parse([text])
    for doc in docs:
        for toponym in doc.toponyms:
            location = toponym.location  # {'name': ..., 'latitude': ..., 'longitude': ..., ...}
            if location:
                # 원하는 형태로 반환 (예: 첫 번째로 찾은 위도·경도만 반환)
                return location['latitude'], location['longitude']
    return None, None


def compute_importance(article_text):
    """기사 텍스트로부터 요약과 중요도 계산"""
    try:
        # 입력 텍스트의 단어 수 확인
        input_length = len(article_text.split())

        # max_length를 입력 텍스트 길이에 따라 조정
        max_length = min(150, int(input_length * 0.8))  # 입력 길이의 80%로 제한
        min_length = max(40, int(input_length * 0.2))  # 입력 길이의 20%로 제한

        # 요약 불가능할 정도로 짧은 텍스트면 min_length나 max_length를 재조정
        if min_length > max_length:
            # 예: 최소값과 최대값을 기본값(5, 20) 정도로 재설정하거나,
            #     아예 요약을 스킵하고 원문 그대로 쓰는 방법도 있음
            min_length = 5
            max_length = 20
        
        # 요약 생성
        summary_result = summarizer(
            article_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
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
