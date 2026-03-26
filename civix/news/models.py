from django.db import models
from location.models import City
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    category_name = models.CharField(max_length=100, null=True, unique=True)
    slug = models.SlugField(unique=True,null=True)

    class Meta:
        db_table = "category"

    def __str__(self):
        return self.category_name
    

# Create your models here.
class News_article(models.Model):
    title = models.CharField(max_length=255, null=False)
    slug = models.CharField(max_length=255, unique=True)
    excerpt = models.TextField(max_length=300)
    content = models.TextField(null=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    author_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    choice = (('draft', 'draft'),("pending", "pending"), ("approved", "approved"), ("rejected", "rejected"))
    status = models.CharField(max_length=20, choices=choice, null=False, default='pending')
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
    rejection_reason = models.TextField(null=True, blank=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:60]
            slug = base_slug
            counter = 1

            while News_article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "news_article"

    def __str__(self):
        return self.title

class ArticleMedia(models.Model):
    article_id = models.ForeignKey(News_article, on_delete=models.CASCADE, related_name="media")
    MEDIA_TYPES = [
        ('image', 'Image') ## in future videos
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default="image")  # e.g., 'image', 'video'
    file = models.FileField(upload_to='newsArticleMedia/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article_media"
    
    def __str__(self):
        return f"{self.article_id.title} - {self.media_type}"

class SavedArticle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(News_article, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saved_article"
    
    def __str__(self):
        return f"{self.article}"

class Comment(models.Model):
    article = models.ForeignKey(News_article, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.TextField(null=False)
    status_choices = (('Active', 'Active'), ('Blocked', 'Blocked'))
    status = models.CharField(max_length=20, choices=status_choices, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comment"

    def __str__(self):
        return f"Comment by {self.user} on {self.article}"