# news/models.py
from django.db import models

class NewsArticle(models.Model):
    CATEGORY_CHOICES = [
        ('business', 'Business'),
        ('entertainment', 'Entertainment'),
        ('general', 'General'),
        ('health', 'Health'),
        ('science', 'Science'),
        ('sports', 'Sports'),
        ('technology', 'Technology'),
    ]

    title = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    importance = models.IntegerField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # 새로 추가: URL 프리뷰 관련 필드
    preview_title = models.CharField(max_length=255, blank=True)
    preview_description = models.TextField(blank=True)
    preview_image = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.title} ({self.category})"
