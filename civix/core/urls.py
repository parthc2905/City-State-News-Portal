from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homePage, name='home'),
    path('signup/', views.userSignupView, name='signup'), 
    path('login/', views.userLoginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    
    # Simplified Password Reset URL (Testing only)
    path('password_reset/', views.simplifiedPasswordResetView, name='password_reset'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),


    path('adminpanel/dashboard/', views.adminPanelDashboardView, name='admin_panel_dashboard'),
    path('adminpanel/applications/', views.adminPanelApplicationsView, name='admin_panel_applications'),
    path('adminpanel/applications/approve/<int:id>', views.adminPanelApplicationsApproval, name='admin_panel_applications_approval'),
    path('adminpanel/applications/reject/<int:id>', views.adminPanelApplicationsReject, name='admin_panel_applications_reject'),
    path('adminpanel/journalists/', views.adminPanelJournalistsView, name='admin_panel_journalists'),
    path('adminpanel/advertisers/', views.adminPanelAdvertisersView, name='admin_panel_advertisers'),
    path('adminpanel/readers/', views.adminPanelReadersView, name='admin_panel_readers'),
    path('journalist/apply/', views.journalistApplicationView, name='journalist_application'),
    path('journalist/pending/', views.journalistPendingView, name='journalist_pending'),
    path('reader/dashboard/', views.readerDashboardView, name='reader_dashboard'),
    path('reader/saved/', views.readerSavedArticlesView, name='reader_saved_articles'),
    path('reader/unsave/<int:article_id>/', views.readerUnsaveArticleView, name='reader_unsave_article'),
    path('reader/profile/', views.readerProfileView, name='reader_profile'),
    path('reader/general/', views.readerGeneralView, name='reader_general'),
    path('article/<slug:slug>/', views.articleDetailView, name='article_detail'),
    path('article/comment/<int:article_id>/', views.addCommentView, name='add_comment'),
    path('latest/', views.latestStoriesView, name='latest_stories'),

    path('state-politics/', views.statePoliticsView, name='state_politics'),
    path('article/save/<int:article_id>/', views.saveArticleView, name='save_article'),
    path('article/report/<int:article_id>/', views.reportArticleView, name='report_article'),
]