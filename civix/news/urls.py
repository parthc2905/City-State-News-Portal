from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('journalist/dashboard/', views.journalistDashboardView, name='journalist_dashboard'),
    path('journalist/write/', views.journalistWriteArticleView, name='journalist_write_article'),
    path('journalist/articles/', views.journalistMyArticlesView, name='journalist_my_articles'),
    path('journalist/profile/', views.journalistProfileView, name='journalist_profile'),
    path('journalist/general/', views.journalistGeneralView, name='journalist_general'),
    path('journalist/writing-guide/', views.journalistWritingGuideView, name='journalist_writing_guide'),

]
