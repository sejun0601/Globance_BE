# news/utils.py
import spacy
from geopy.geocoders import Nominatim
from newsapi import NewsApiClient
from transformers import pipeline

nlp = spacy.load('en_core_web_sm')
geolocator = Nominatim(user_agent="geoapiExercises")
newsapi = NewsApiClient(api_key='YOUR_API_KEY')  # API 키 교체

# BART 기반 요약 파이프라인 전역 초기화
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")



def fetch_articles(category='general', country='us', language='en', page_size=20, page=1):
    response = newsapi.get_top_headlines(
        category=category,
        country=country,
        language=language,
        page_size=page_size,
        page=page
    )
    return response.get('articles', [])


def extract_location(text):
    """텍스트에서 위치 엔티티 추출 및 지오코딩하여 (lat, lon) 반환."""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:  # 장소 관련 엔티티
            location_name = ent.text
            location = geolocator.geocode(location_name)
            if location:
                return (location.latitude, location.longitude)
    return None


def compute_importance(article_text):
    # 기사 요약 생성
    try:
        summary_result = summarizer(article_text, max_length=150, min_length=40, do_sample=False)
        summary = summary_result[0]['summary_text']
    except Exception as e:
        print("요약 생성 중 오류 발생:", e)
        summary = ""

    # 요약문의 단어 수를 기반으로 중요도 점수 계산
    importance_score = len(summary.split())

    return summary, importance_score


def articles_to_geojson(articles):
    features = []
    for article in articles:
        # 기사 본문이나 설명에서 위치 정보 추출
        content = article.get('description') or article.get('title', '')
        coords = extract_location(content)

        # 위치 정보를 찾지 못하면 스킵
        if not coords:
            continue

        importance = compute_importance(article)

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [coords[1], coords[0]]  # GeoJSON은 [lon, lat]
            },
            "properties": {
                "title": article.get('title'),
                "url": article.get('url'),
                "description": article.get('description'),
                "importance": importance,
                # 필요시 더 많은 속성 추가
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson
