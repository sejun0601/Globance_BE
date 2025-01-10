# news/views.py
from .models import NewsArticle
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Subquery


# news/views.py

class ArticlesGeoJSON(APIView):
    def get(self, request):
        category = request.GET.get('category')
        if category:
            if category not in dict(NewsArticle.CATEGORY_CHOICES):
                return Response({'error': 'Invalid category'}, status=400)
            base_articles = NewsArticle.objects.filter(
                category=category,
                latitude__isnull=False,
                longitude__isnull=False
            )
        else:
            base_articles = NewsArticle.objects.exclude(
                latitude__isnull=True,
                longitude__isnull=True
            )

        # 클라이언트로부터 limit 파라미터 가져오기 (기본값: 30)
        limit_param = request.GET.get('limit', '30')
        try:
            limit = int(limit_param)
        except ValueError:
            limit = 30  # 유효한 정수가 아니면 기본값 사용

        # 발행일 기준으로 최신 기사 limit개 선택 (서브쿼리)
        latest_articles_subquery = base_articles.order_by("-published_at").values("pk")[:limit]

        # 서브쿼리로 선택된 기사들 중 중요도 순으로 정렬
        articles = NewsArticle.objects.filter(
            pk__in=Subquery(latest_articles_subquery)
        ).order_by("-importance")

        features = []
        for article in articles:
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
                    "published_at": article.published_at.isoformat() if article.published_at else None,
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
