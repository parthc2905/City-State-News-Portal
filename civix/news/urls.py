from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('journalist/dashboard/', views.journalistDashboardView, name='journalist_dashboard'),
    path('journalist/write/', views.journalistWriteArticleView, name='journalist_write_article'),
    path('journalist/articles/', views.journalistMyArticlesView, name='journalist_my_articles'),
    path('journalist/profile/', views.journalistProfileView, name='journalist_profile'),
    path('journalist/general/', views.journalistGeneralView, name='journalist_general'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)