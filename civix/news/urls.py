from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('journalist/dashboard/', views.journalistDashboardView, name='journalist_dashboard'),
    path('journalist/write/', views.journalistWriteArticleView, name='journalist_write_article'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)