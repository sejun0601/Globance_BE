# news/views.py
from .models import NewsArticle
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone

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

        all_articles = []
        for cat in valid_requested:
            # 1) 해당 카테고리의 좌표가 있는 기사 중, 최신순으로 limit 개
            cat_articles = (
                NewsArticle.objects
                .filter(
                    category=cat,
                    latitude__isnull=False,
                    longitude__isnull=False
                )
                .order_by("-published_at")[:limit]
            )

            # 2) 가져온 기사들을 중요도 순으로 정렬
            cat_articles = sorted(cat_articles, key=lambda x: x.importance, reverse=True)

            # 3) 리스트에 추가
            all_articles.extend(cat_articles)

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
                    "category": article.category,
                    
                    # 프리뷰 관련 필드를 함께 포함 (이미 NewsArticle 모델에 존재한다고 가정)
                    "preview_title": article.preview_title,
                    "preview_description": article.preview_description,
                    "preview_image": article.preview_image,
                }
            }
            features.append(feature)

        return Response({
            "type": "FeatureCollection",
            "features": features
        })

class WeeklyTopSummaries(APIView):
    """
    지난 7일 안에 있었던 뉴스 중,
    중요도가 높은 순으로 최대 'limit'개의 뉴스 요약을
    모두 합쳐서 반환하는 뷰.
    """
    def get(self, request):
        # 1) "7일 전" 시점 계산
        one_week_ago = timezone.now() - timedelta(days=7)

        # 2) 쿼리 파라미터로부터 limit 값을 가져오고, 기본값은 10
        limit_str = request.GET.get('limit', '3')
        try:
            limit = int(limit_str)
        except ValueError:
            limit = 10

        # 3) 지난 7일간 발행된 기사 중 중요도 높은 순으로 limit 개
        top_articles = (
            NewsArticle.objects
            .filter(published_at__gte=one_week_ago)
            .order_by('-importance')[:limit]
        )

        # 4) 각 기사(summary 필드)의 내용을 모두 합치기
        #    원하는 구분자(\n, \n\n 등)로 합쳐서 문자열 생성 가능
        combined_summaries = "\n\n".join(
            article.summary for article in top_articles if article.summary
        )

        # 5) Response 반환
        return Response({
            "combined_summaries": combined_summaries,
            "limit": limit,
        })