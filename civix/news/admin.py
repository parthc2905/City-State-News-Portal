from django.contrib import admin
from .models import Category, News_article, ArticleMedia, SavedArticle, Comment

# Register your models here.
admin.site.register(Category)
admin.site.register(News_article)
admin.site.register(ArticleMedia)
admin.site.register(SavedArticle)
admin.site.register(Comment)

