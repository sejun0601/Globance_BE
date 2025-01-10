# news/views.py
from .models import NewsArticle
from rest_framework.views import APIView
from rest_framework.response import Response


# news/views.py

class ArticlesGeoJSON(APIView):
    def get(self, request):
        category = request.GET.get('category')
        if category:
            if category not in dict(NewsArticle.CATEGORY_CHOICES):
                return Response({'error': 'Invalid category'}, status=400)
            articles = NewsArticle.objects.filter(category=category, latitude__isnull=False, longitude__isnull=False)
        else:
            articles = NewsArticle.objects.exclude(latitude__isnull=True, longitude__isnull=True)

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

