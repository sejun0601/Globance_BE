# news/views.py
from .models import NewsArticle
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Subquery


# news/views.py

class ArticlesGeoJSON(APIView):
    def get(self, request):
        # 클라이언트에서 ?category=business&category=health 식으로 여러 파라미터를 받는 경우
        category_list = request.GET.getlist('category')  # 여러 값이 리스트로 들어옴
        valid_choices = {choice[0] for choice in NewsArticle.CATEGORY_CHOICES}

        if category_list:
            # 유효한 카테고리만 필터링
            valid_requested = [c for c in category_list if c in valid_choices]
            if not valid_requested:
                return Response({'error': 'No valid categories provided'}, status=400)
        else:
            # 카테고리 파라미터가 없으면 전체 카테고리를 대상으로 한다고 가정
            valid_requested = list(valid_choices)

        # limit 파라미터 처리 (기본값 30)
        limit_param = request.GET.get('limit', '30')
        try:
            limit = int(limit_param)
        except ValueError:
            limit = 30

        # --- 핵심 변경점 ---
        # 각 카테고리마다 "최신순(limit만큼)"으로 우선 추출 -> 그 후 "중요도 순으로" 재정렬.
        all_articles = []
        for cat in valid_requested:
            # 1) 해당 카테고리의 좌표가 있는 기사 중, 최신순으로 limit 개
            cat_articles = (NewsArticle.objects
                            .filter(
                                category=cat,
                                latitude__isnull=False,
                                longitude__isnull=False
                            )
                            .order_by("-published_at")[:limit])

            # 2) 위에서 뽑은 기사들을 중요도 순으로 다시 정렬 (파이썬 정렬 사용)
            #    (쿼리셋 슬라이싱 후에는 파이썬 list로 다루게 되므로 sorted() 사용 가능)
            cat_articles = sorted(cat_articles, key=lambda x: x.importance, reverse=True)

            # 3) 최종 리스트에 추가
            all_articles.extend(cat_articles)

        # 이제 all_articles에는 "카테고리별로 최신순->중요도순" 정렬된 기사들이 모두 들어 있음
        # (카테고리 순서대로 합쳐져 있음)

        # GeoJSON 결과 생성
        features = []
        for article in all_articles:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [article.longitude, article.latitude]
                },
                "properties": {
                    "title": article.title,
                    "description": article.description,
                    "url": article.url,
                    "published_at": (
                        article.published_at.isoformat() if article.published_at else None
                    ),
                    "summary": article.summary,
                    "importance": article.importance,
                    "category": article.category
                }
            }
            features.append(feature)

        return Response({
            "type": "FeatureCollection",
            "features": features
        })