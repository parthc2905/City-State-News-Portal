from django.db import models
from location.models import State, City
from django.conf import settings

class Category(models.Model):
    category_name = models.CharField(max_length=100, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Category"

    def __str__(self):
        return self.category_name
    

# Create your models here.
class News_article(models.Model):
    title = models.CharField(max_length=255, null=False)
    slug = models.CharField(max_length=255, unique=True)
    excerpt = models.TextField(max_length=300)
    content = models.TextField(null=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    state_id = models.ForeignKey(State, on_delete=models.CASCADE)
    city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    author_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    choice = (("pending", "pending"), ("approved", "approved"), ("rejected", "rejected"))
    status = models.CharField(max_length=20, choices=choice, null=False)
    is_draft = models.BooleanField(default=True)
    VISIBILITY_CHOICES = [
    ("public", "Public"),
    ("private", "Private"),
    ("subscriber", "Subscribers Only"),
    ]

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="public"
    )
    is_breaking = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "news_article"

    def __str__(self):
        return self.title

class ArticleMedia(models.Model):
    article_id = models.ForeignKey(News_article, on_delete=models.CASCADE)
    MEDIA_TYPES = [
        ('image', 'Image') ## in future videos
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)  # e.g., 'image', 'video'
    file = models.FileField(upload_to='newsArticleMedia/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article_media"
    
    def __str__(self):
        return f"{self.article_id.title} - {self.media_type}"
    