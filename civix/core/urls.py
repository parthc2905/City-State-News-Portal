from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name='home'),
    path('signup/', views.userSignupView, name='signup'), 
    path('login/', views.userLoginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('adminpanel/dashboard/', views.adminPanelDashboardView, name='admin_panel_dashboard'),
    path('adminpanel/applications/', views.adminPanelApplicationsView, name='admin_panel_applications'),
    path('adminpanel/applications/approve/<int:id>', views.adminPanelApplicationsApproval, name='admin_panel_applications_approval'),
    path('adminpanel/applications/reject/<int:id>', views.adminPanelApplicationsReject, name='admin_panel_applications_reject'),
    path('adminpanel/journalists/', views.adminPanelJournalistsView, name='admin_panel_journalists'),
    path('adminpanel/advertisers/', views.adminPanelAdvertisersView, name='admin_panel_advertisers'),
    path('adminpanel/readers/', views.adminPanelReadersView, name='admin_panel_readers'),
    path('reader/dashboard/', views.readerDashboardView, name='reader_dashboard'),
    path('article/<slug:slug>/', views.articleDetailView, name='article_detail'),
    path('latest/', views.latestStoriesView, name='latest_stories'),
    path('state-politics/', views.statePoliticsView, name='state_politics'),
    path('article/save/<int:article_id>/', views.saveArticleView, name='save_article'),
    path('article/report/<int:article_id>/', views.reportArticleView, name='report_article'),
]