from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('journalist/dashboard/', views.journalistDashboardView, name='journalist_dashboard'),
    path('journalist/write/', views.journalistWriteArticleView, name='journalist_write_article'),
    path('journalist/articles/', views.journalistMyArticlesView, name='journalist_my_articles'),
    path('journalist/articles/preview/<int:article_id>/', views.journalistArticlePreviewView, name='journalist_article_preview'),
    path('journalist/articles/edit/<int:article_id>/', views.journalistEditArticleView, name='journalist_edit_article'),
    path('journalist/articles/delete/<int:article_id>/', views.journalistDeleteArticleView, name='journalist_delete_article'),
    path('journalist/profile/', views.journalistProfileView, name='journalist_profile'),
    path('journalist/general/', views.journalistGeneralView, name='journalist_general'),
    path('journalist/writing-guide/', views.journalistWritingGuideView, name='journalist_writing_guide'),

]
