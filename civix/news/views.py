from location.models import State, City
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from reports.models import CitizenReport
from .models import News_article, ArticleMedia, Category, SavedArticle


def journalistDashboardView(request):
    return redirect("journalist_write_article")


def journalistArticlePreviewView(request, article_id):
    article = get_object_or_404(
        News_article.objects.prefetch_related("media"),
        id=article_id,
        author_id=request.user,
    )
    return render(request, "journalist/journalistArticlePreview.html", {"article": article})


def journalistWriteArticleView(request):
    if request.method == "POST":
        article = ArticleWriteForm(request.POST)
        articleMedia = ArticleMediaForm(request.POST, request.FILES)
        if article.is_valid() and articleMedia.is_valid():
            article_obj = article.save(commit=False)
            article_obj.author_id_id = request.user.id
            article_obj.save()

            if request.FILES.get("file"):
                media_obj = articleMedia.save(commit=False)
                media_obj.article_id_id = article_obj.id
                media_obj.save()
    else:
        article = ArticleWriteForm()
        articleMedia = ArticleMediaForm()

    return render(
        request,
        "journalist/journalistWriteArticle.html",
        {"articleForm": article, "articleMedia": articleMedia},
    )


def journalistEditArticleView(request, article_id):
    article_obj = get_object_or_404(
        News_article, id=article_id, author_id=request.user
    )

    if request.method == "POST":
        article = ArticleWriteForm(request.POST, instance=article_obj)
        articleMedia = ArticleMediaForm(request.POST, request.FILES)
        if article.is_valid() and articleMedia.is_valid():
            article.save()

            if request.FILES.get("file"):
                # Remove old media and save new one
                ArticleMedia.objects.filter(article_id=article_obj).delete()
                media_obj = articleMedia.save(commit=False)
                media_obj.article_id_id = article_obj.id
                media_obj.save()

            messages.success(request, "Article updated successfully!")
            return redirect("journalist_my_articles")
    else:
        # Map status back to publication_status form field
        pub_status = "draft" if article_obj.status == "draft" else "published"
        article = ArticleWriteForm(
            instance=article_obj,
            initial={"publication_status": pub_status},
        )
        articleMedia = ArticleMediaForm()

    return render(
        request,
        "journalist/journalistWriteArticle.html",
        {
            "articleForm": article,
            "articleMedia": articleMedia,
            "editing": True,
            "article_obj": article_obj,
        },
    )


def journalistDeleteArticleView(request, article_id):
    article = get_object_or_404(
        News_article, id=article_id, author_id=request.user
    )
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted successfully!")
    return redirect("journalist_my_articles")


def journalistMyArticlesView(request):
    base_qs = News_article.objects.filter(author_id=request.user)
    # --- filters from GET ---
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all")
    category = request.GET.get("category", "all")
    sort = request.GET.get("sort", "newest")
    if status != "all":
        # map UI values to DB values
        status_map = {
            "published": "approved",
            "draft": "draft",
            "review": "pending",
            "rejected": "rejected",
        }
        db_status = status_map.get(status)
        if db_status:
            base_qs = base_qs.filter(status=db_status)
    if category != "all":
        base_qs = base_qs.filter(category_id__category_name__iexact=category)

    # --- stats: computed BEFORE search so analytics cards stay month-based ---
    stats_qs = base_qs  # no search filter applied yet
    total = stats_qs.count()
    published = stats_qs.filter(status="approved").count()
    drafts = stats_qs.filter(status="draft").count()
    in_review = stats_qs.filter(status="pending").count()
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = stats_qs.filter(created_at__gte=start_of_month).count()
    percent_published = int(published * 100 / total) if total else 0
    stats = {
        "total": total,
        "published": published,
        "drafts": drafts,
        "in_review": in_review,
        "new_this_month": new_this_month,
        "percent_published": percent_published,
    }

    # --- apply search filter AFTER stats (only affects article list) ---
    if search:
        base_qs = base_qs.filter(title__icontains=search)
    if sort == "oldest":
        base_qs = base_qs.order_by("created_at")
    elif sort == "views":
        base_qs = base_qs.order_by("-views_count")
    elif sort == "title":
        base_qs = base_qs.order_by("title")
    else:  # newest
        base_qs = base_qs.order_by("-created_at")

    articles = base_qs.prefetch_related("media")
    # Get categories the user has written articles for
    user_categories = Category.objects.filter(news_article__author_id=request.user).distinct()
    # Get remaining categories
    other_categories = Category.objects.exclude(id__in=user_categories.values('id'))

    context = {
        "articles": articles,
        "stats": stats,
        "current": {
            "q": search,
            "status": status,
            "category": category,
            "sort": sort,
        },
        "user_categories": user_categories,
        "other_categories": other_categories,
    }
    return render(request, "journalist/journalistMyArticles.html", context)


def journalistDraftsView(request):
    base_qs = News_article.objects.filter(author_id=request.user)
    search = request.GET.get("q", "").strip()
    status = "draft"
    category = request.GET.get("category", "all")
    sort = request.GET.get("sort", "newest")
    
    base_qs = base_qs.filter(status="draft")
    
    if category != "all":
        base_qs = base_qs.filter(category_id__category_name__iexact=category)

    stats_qs = News_article.objects.filter(author_id=request.user)
    total = stats_qs.count()
    published = stats_qs.filter(status="approved").count()
    drafts = stats_qs.filter(status="draft").count()
    in_review = stats_qs.filter(status="pending").count()
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = stats_qs.filter(created_at__gte=start_of_month).count()
    percent_published = int(published * 100 / total) if total else 0
    stats = {
        "total": total,
        "published": published,
        "drafts": drafts,
        "in_review": in_review,
        "new_this_month": new_this_month,
        "percent_published": percent_published,
    }

    if search:
        base_qs = base_qs.filter(title__icontains=search)
    if sort == "oldest":
        base_qs = base_qs.order_by("created_at")
    elif sort == "views":
        base_qs = base_qs.order_by("-views_count")
    elif sort == "title":
        base_qs = base_qs.order_by("title")
    else:
        base_qs = base_qs.order_by("-created_at")

    articles = base_qs.prefetch_related("media")
    user_categories = Category.objects.filter(news_article__author_id=request.user).distinct()
    other_categories = Category.objects.exclude(id__in=user_categories.values('id'))

    context = {
        "articles": articles,
        "stats": stats,
        "current": {
            "q": search,
            "status": status,
            "category": category,
            "sort": sort,
        },
        "user_categories": user_categories,
        "other_categories": other_categories,
        "is_drafts_page": True,
    }
    return render(request, "journalist/journalistMyArticles.html", context)


def journalistProfileView(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.phone = request.POST.get("phone", user.phone)
        
        profile.bio = request.POST.get("bio", profile.bio)
        state_id = request.POST.get("state")
        city_id = request.POST.get("city")
        if state_id:
            profile.state_id = state_id
        if city_id:
            profile.city_id = city_id
        
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            fs = FileSystemStorage()
            from django.conf import settings
            
            if profile.profile_image:
                old_name = profile.profile_image.replace(settings.MEDIA_URL, "")
                if fs.exists(old_name):
                    fs.delete(old_name)
                    
            filename = fs.save(f"profile_images/{user.id}_{avatar.name}", avatar)
            profile.profile_image = fs.url(filename)
            
        user.save()
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("journalist_profile")

    states = State.objects.all()
    cities = City.objects.all()
    
    return render(request, "journalist/journalistProfile.html", {
        "states": states,
        "cities": cities,
        "profile": profile,
    })


def journalistWritingGuideView(request):
    return render(request, "journalist/journalistWritingGuide.html")


def journalistGeneralView(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "update_notifications" in request.POST:
            profile.email_notifications = request.POST.get("email_notifications") == "on"
            profile.breaking_news_alerts = request.POST.get("breaking_news_alerts") == "on"
            profile.weekly_newsletter = request.POST.get("weekly_newsletter") == "on"
            profile.article_recommendations = request.POST.get("article_recommendations") == "on"
            profile.save()
            messages.success(request, "Notification preferences updated successfully.")
            return redirect("journalist_general")
            
        elif "update_password" in request.POST:
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password and new_password == confirm_password:
                user = request.user
                user.set_password(new_password)
                user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match.")
            return redirect("journalist_general")
            
        elif "delete_account" in request.POST:
            user = request.user
            user.delete()
            return redirect("/")  # Redirect to home/login after deletion

    return render(request, "journalist/journalistGeneral.html", {"profile": profile})


# @login_required
# @require_POST
def save_article_view(request, article_id):
    article = get_object_or_404(News_article, id=article_id)
    saved_article, created = SavedArticle.objects.get_or_create(user=request.user, article=article)
    
    if not created:
        saved_article.delete()
        return JsonResponse({'status': 'unsaved', 'message': 'Article removed from your library.'})
    
    return JsonResponse({'status': 'saved', 'message': 'Article saved to your library!'})


# @login_required
# @require_POST
def report_article_view(request, article_id):
    article = get_object_or_404(News_article, id=article_id)
    reason = request.POST.get('description', '').strip()
    
    if not reason:
        return JsonResponse({'status': 'error', 'message': 'Please provide a reason for reporting.'}, status=400)
    
    # Use article's location for the report
    CitizenReport.objects.create(
        user=request.user,
        article=article,
        title=f"Report: {article.title}",
        description=reason,
        state=article.city_id.state_id,
        city=article.city_id,
        status='pending'
    )
    
    return JsonResponse({'status': 'success', 'message': 'Thank you for reporting. Our moderators will review it soon.'})