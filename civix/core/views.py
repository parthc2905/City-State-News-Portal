from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from .forms import (
    UserSignupForm,
    UserLoginForm,
    CommentForm,
    JournalistIdentityForm,
    JournalistProfileLocationForm,
    JournalistApplicationDocumentsForm,
)
from .models import User, Profile, JournalistApplication
from ads.models import AdvertiserApplication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, F, Count
from django.db.models.functions import TruncMonth
from news.models import News_article, SavedArticle, Comment
from reports.models import CitizenReport
from location.models import State, City
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.urls import reverse

def articleDetailView(request, slug):
    # Fetch article - allow admin to see non-approved articles
    article_qs = News_article.objects.prefetch_related('media').select_related(
        'author_id', 'category_id', 'city_id__state_id'
    )
    
    # Try to find the article by slug
    article = get_object_or_404(article_qs, slug=slug)

    # Permission check: If article is not approved, only admin or the author can see it
    if article.status != 'approved':
        if not request.user.is_authenticated or (request.user.role != 'admin' and request.user != article.author_id):
            raise Http404()

    # Increment view count
    News_article.objects.filter(pk=article.pk).update(views_count=F('views_count') + 1)
    article.views_count += 1

    # Compute read time
    word_count = len(article.content.split())
    article.read_time = max(1, word_count // 200)

    # Left sidebar: top trending articles in the same category (excl. current)
    left_articles = (
        News_article.objects
        .filter(status='approved', category_id=article.category_id)
        .exclude(pk=article.pk)
        .prefetch_related('media')
        .select_related('author_id', 'category_id')
        .order_by('-views_count')[:4]
    )
    for a in left_articles:
        a.read_time = max(1, len(a.content.split()) // 200)

    # Right sidebar: latest articles excluding current + left sidebar articles
    excluded_ids = [article.pk] + [a.pk for a in left_articles]
    right_articles = (
        News_article.objects
        .filter(status='approved')
        .exclude(pk__in=excluded_ids)
        .prefetch_related('media')
        .select_related('author_id', 'category_id')
        .order_by('-created_at')[:4]
    )
    for a in right_articles:
        a.read_time = max(1, len(a.content.split()) // 200)

    return render(request, 'base/articleDetail.html', {
        'article': article,
        'left_articles': left_articles,
        'right_articles': right_articles,
        'comment_form': CommentForm(),
    })




def latestStoriesView(request):
    all_articles = list(
        News_article.objects
        .filter(status='approved')
        .prefetch_related('media')
        .select_related('author_id', 'category_id', 'city_id__state_id')
        .order_by('-created_at')
    )
    for a in all_articles:
        a.read_time = max(1, len(a.content.split()) // 200)

    hero = all_articles[0] if all_articles else None
    rest  = all_articles[1:]
    left_articles  = rest[::2][:2]   # Limit to top 2 odd-index articles
    right_articles = rest[1::2][:2]  # Limit to top 2 even-index articles

    return render(request, 'base/latestStories.html', {
        'hero': hero,
        'left_articles': left_articles,
        'right_articles': right_articles,
    })


def statePoliticsView(request):
    all_articles = list(
        News_article.objects
        .filter(status='approved', category_id__category_name__icontains='Politic')
        .prefetch_related('media')
        .select_related('author_id', 'category_id', 'city_id__state_id')
        .order_by('-created_at')
    )
    for a in all_articles:
        a.read_time = max(1, len(a.content.split()) // 200)

    hero = all_articles[0] if all_articles else None
    rest = all_articles[1:]
    left_articles = rest[::2][:3]   # Showing more in see-all
    right_articles = rest[1::2][:3] # Showing more in see-all

    return render(request, 'base/statePolitics.html', {
        'hero': hero,
        'left_articles': left_articles,
        'right_articles': right_articles,
    })


def homePage(request):
    hero_article = News_article.objects.filter(status='approved').order_by('-created_at').first()
    
    if hero_article:
        word_count = len(hero_article.content.split())
        hero_article.read_time = max(1, word_count // 200)
        trending_articles = News_article.objects.filter(status='approved').exclude(id=hero_article.id).order_by('-views_count')[:5]
    else:
        trending_articles = News_article.objects.filter(status='approved').order_by('-views_count')[:5]
        
    for article in trending_articles:
        word_count = len(article.content.split())
        article.read_time = max(1, word_count // 200)
        
    excluded_ids = [a.id for a in trending_articles]
    if hero_article:
        excluded_ids.append(hero_article.id)
        
    latest_articles = News_article.objects.filter(status='approved').exclude(id__in=excluded_ids).order_by('-created_at')[:6]
    for article in latest_articles:
        word_count = len(article.content.split())
        article.read_time = max(1, word_count // 200)
        
    excluded_ids.extend([a.id for a in latest_articles])
    
    state_politics_articles = News_article.objects.filter(status='approved', category_id__category_name__icontains='Politic').exclude(id__in=excluded_ids).order_by('-created_at')[:4]
    for article in state_politics_articles:
        word_count = len(article.content.split())
        article.read_time = max(1, word_count // 200)
        
    excluded_ids.extend([a.id for a in state_politics_articles])
    
    politics_sidebar_articles = News_article.objects.filter(status='approved', category_id__category_name__icontains='Politic').exclude(id__in=excluded_ids).order_by('-views_count')[:3]
    for article in politics_sidebar_articles:
        word_count = len(article.content.split())
        article.read_time = max(1, word_count // 200)

    return render(request, 'base/base.html', {
        'hero_article': hero_article,
        'trending_articles': trending_articles,
        'latest_articles': latest_articles,
        'state_politics_articles': state_politics_articles,
        'politics_sidebar_articles': politics_sidebar_articles,
    })

# signup view for user registration
def userSignupView(request):
    active_tab = "signup"

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
    
        if form.is_valid():

            #email send
            email = form.cleaned_data['email']
            send_mail(subject="welcome to find my newspaper",message="Thank you for registering with CIVIX.",from_email=settings.EMAIL_HOST_USER,recipient_list=[email])
            
            user = form.save(commit=False)
            # ADD approval status for reader to not_required in db while sigup
            if user.role == 'reader':
                user.approval_status = 'not_required'

            user.save()

            # It Will return to login urls
            return redirect('login') 
        else:
            return render(request,'auth/signupsignin.html',{'form':form ,"active_tab": active_tab })
    else:
        form = UserSignupForm()
        return render(request, 'auth/signupsignin.html', {'form': form, "active_tab": active_tab})


# login view for user authentication
def userLoginView(request):
    active_tab = "signin"
    if request.method == 'POST':
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # print(email,password)
            user = authenticate(request, email=email, password=password)
            # print(user)
            if user:
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin_panel_dashboard') # Replace with your admin dashboard URL name
                elif user.role == 'reader':
                    # print(user)
                    return redirect('home') # Replace with your reader dashboard URL name
                elif user.role == 'journalist':
                    if user.approval_status == 'approved':
                        return redirect('home')
                    else:
                        if not hasattr(user, 'journalist_application'):
                            return redirect('journalist_application')
                        else:
                            return redirect('journalist_pending')
                elif user.role == 'advertiser':
                    return redirect('advertiser_dashboard')
            else:
                return render(request,'auth/signupsignin.html',{'form':form,"active_tab": active_tab}) 
    else:
        form = UserLoginForm()
        return render(request, 'auth/signupsignin.html', {'form': form ,"active_tab": active_tab})   


def logoutView(request):
    logout(request)
    return redirect('home')

@role_required(allowed_roles=["admin"])
def adminPanelDashboardView(request):
    # --- Applications Stats ---
    apps_qs = User.objects.filter(role__in=['journalist', 'advertiser'])
    app_stats = {
        'total': apps_qs.count(),
        'pending': apps_qs.filter(approval_status='pending').count(),
        'approved': apps_qs.filter(approval_status='approved').count(),
        'rejected': apps_qs.filter(approval_status='rejected').count(),
    }
    
    app_roles = list(apps_qs.values('role').annotate(count=Count('id')))
    app_status = list(apps_qs.values('approval_status').annotate(count=Count('id')))

    # --- Articles Stats ---
    articles_qs = News_article.objects.all()
    article_stats = {
        'total': articles_qs.count(),
        'approved': articles_qs.filter(status='approved').count(),
        'pending': articles_qs.filter(status='pending').count(),
        'reported': articles_qs.filter(article_reports__isnull=False).distinct().count(),
    }
    
    article_status = list(articles_qs.values('status').annotate(count=Count('id')))
    category_dist = list(articles_qs.values('category_id__category_name').annotate(count=Count('id')))
    
    # --- Comments Stats ---
    comments_qs = Comment.objects.all()
    comment_stats = {
        'total': comments_qs.count(),
        'active': comments_qs.filter(status='Active').count(),
        'blocked': comments_qs.filter(status='Blocked').count(),
        'reported': comments_qs.filter(comment_reports__isnull=False).distinct().count(),
    }

    # --- Timeline Data ---
    from datetime import timedelta
    six_months_ago = timezone.now() - timedelta(days=180)
    
    articles_timeline = list(
        News_article.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    users_timeline = list(
        User.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    context = {
        'stats': {
            'apps': app_stats,
            'articles': article_stats,
            'comments': comment_stats,
        },
        'charts': {
            'app_roles': app_roles,
            'app_status': app_status,
            'article_status': article_status,
            'category_dist': category_dist,
            'articles_timeline': [
                {'month': item['month'].strftime('%b %Y'), 'count': item['count']} 
                for item in articles_timeline
            ],
            'users_timeline': [
                {'month': item['month'].strftime('%b %Y'), 'count': item['count']} 
                for item in users_timeline
            ],
        }
    }
    return render(request, 'adminPanel/adminPanelOverview.html', context)


def adminPanelApplicationsView(request):
    from datetime import timedelta
    from .models import JournalistApplication

    query = request.GET.get("q", "").strip()
    tab = request.GET.get("tab", "all").strip()  # all | journalists | advertisers | pending

    base_qs = User.objects.filter(role__in=["journalist", "advertiser"])

    # --- Stats (computed from DB; independent of q/tab) ---
    pending_count = base_qs.filter(approval_status="pending").count()
    journalists_count = base_qs.filter(role="journalist").count()
    advertisers_count = base_qs.filter(role="advertiser").count()
    total_count = base_qs.count()

    now = timezone.now()
    start_of_week = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    approved_this_week = base_qs.filter(
        approval_status="approved",
        updated_at__gte=start_of_week,
    ).count()
    rejected_this_week = base_qs.filter(
        approval_status="rejected",
        updated_at__gte=start_of_week,
    ).count()

    reviewed_qs = (
        base_qs.filter(approval_status__in=["approved", "rejected"])
        .select_related("journalist_application")
    )
    durations_days = []
    for user in reviewed_qs.iterator():
        submitted_at = user.created_at
        if user.role == "journalist":
            try:
                submitted_at = user.journalist_application.submitted_at
            except JournalistApplication.DoesNotExist:
                submitted_at = user.created_at

        diff_seconds = (user.updated_at - submitted_at).total_seconds()
        diff_days = diff_seconds / (24 * 3600)
        if diff_days >= 0:
            durations_days.append(diff_days)

    avg_review_time_days = round(sum(durations_days) / len(durations_days), 1) if durations_days else 0.0

    stats = {
        "pending": pending_count,
        "approved_this_week": approved_this_week,
        "rejected_this_week": rejected_this_week,
        "avg_review_time_days": avg_review_time_days,
    }

    toolbar_counts = {
        "all": total_count,
        "journalists": journalists_count,
        "advertisers": advertisers_count,
        "pending": pending_count,
    }


    if query:
        users = User.objects.filter(role__in=["journalist", "advertiser"])
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        users = users.order_by("-id")
    else:
        users = User.objects.filter(role__in=['journalist', 'advertiser']).order_by('id')



    # --- Apply tab filter to the list ---
    if tab == "journalists":
        users = users.filter(role="journalist")
    elif tab == "advertisers":
        users = users.filter(role="advertiser")
    elif tab == "pending":
        users = users.filter(approval_status="pending")

    return render(
        request,
        "adminPanel/adminPanelApplications.html",
        {
            "users": users,
            "stats": stats,
            "toolbar_counts": toolbar_counts,
            "current": {"q": query, "tab": tab},
        },
    )


def _format_datetime_display(dt):
    """Format datetimes for the admin modal preview."""
    if not dt:
        return "-"
    local_dt = timezone.localtime(dt)
    return local_dt.strftime("%b %d, %Y %I:%M %p")


@role_required(allowed_roles=["admin"])
def adminPanelApplicationPreviewView(request, id):
    user = get_object_or_404(User, id=id)

    data = {
        "type": user.role,
        "application_id": f"{'JRN' if user.role == 'journalist' else 'ADV'}-{user.id}",
        "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or "-",
        "email": user.email or "-",
        "phone": user.phone or "-",
        "applied_on_display": _format_datetime_display(user.created_at),
        "rejection_reason": "-",
        "documents": [],
    }

    if user.role == "journalist":
        try:
            app = user.journalist_application
        except Exception:
            app = None

        if app:
            data["applied_on_display"] = _format_datetime_display(app.submitted_at)

            document_rows = [
                ("Aadhaar ID", getattr(app, "aadhaar_file", None), bool(getattr(app, "aadhaar_verified", False))),
                ("Portfolio", getattr(app, "portfolio_file", None), bool(getattr(app, "portfolio_verified", False))),
                ("Press Card", getattr(app, "press_card_file", None), bool(getattr(app, "press_card_verified", False))),
                ("Recommendation", getattr(app, "recommendation_file", None), bool(getattr(app, "recommendation_verified", False))),
            ]

            docs_out = []
            for label, file_obj, verified in document_rows:
                url = None
                try:
                    if file_obj:
                        url = file_obj.url
                except Exception:
                    url = None

                if url:
                    docs_out.append({
                        "label": label,
                        "verified": verified,
                        "url": url,
                        "slug": label.lower().replace(" ", "_")
                    })

            data["documents"] = docs_out
            if app.rejection_reason:
                data["rejection_reason"] = app.rejection_reason

    elif user.role == "advertiser":
        try:
            app = user.advertiser_application
        except AdvertiserApplication.DoesNotExist:
            app = None
        
        if app:
            data["applied_on_display"] = _format_datetime_display(app.submitted_at)
            data["full_name"] = f"{app.contact_name} ({app.designation})"
            # Set phone from application if user phone is missing
            if not data["phone"] or data["phone"] == "-":
                data["phone"] = app.phone
            
            data["company_info"] = {
                "name": app.company_name,
                "type": app.business_type,
                "size": app.company_size,
                "gst": app.gst_number,
                "website": app.website or "-",
                "budget": app.budget_range,
            }
            
            document_rows = [
                ("Registration", app.registration_certificate, getattr(app, "registration_verified", False)),
                ("GST Certificate", app.gst_certificate, getattr(app, "gst_verified", False)),
                ("PAN Card", app.pan_card, getattr(app, "pan_verified", False)),
                ("Bank Details", app.bank_details, getattr(app, "bank_verified", False)),
            ]
            
            docs_out = []
            for label, file_obj, verified in document_rows:
                url = None
                try:
                    if file_obj:
                        url = file_obj.url
                except Exception:
                    url = None
                if url:
                    docs_out.append({
                        "label": label, 
                        "verified": verified, 
                        "url": url,
                        "slug": label.lower().replace(" ", "_")
                    })
            
            data["documents"] = docs_out
            if app.rejection_reason:
                data["rejection_reason"] = app.rejection_reason

    return JsonResponse(data)


def adminPanelApplicationsApproval(request,id):
    user = get_object_or_404(User,id=id)

    # SECURE FLOW: Ensure documents are verified before final approval
    unverified = []
    if user.role == "journalist":
        app = getattr(user, 'journalist_application', None)
        if app:
            if app.aadhaar_file and not app.aadhaar_verified: unverified.append("Aadhaar")
            if app.portfolio_file and not app.portfolio_verified: unverified.append("Portfolio")
            if app.press_card_file and not app.press_card_verified: unverified.append("Press Card")
            if app.recommendation_file and not app.recommendation_verified: unverified.append("Recommendation")
    elif user.role == "advertiser":
        app = getattr(user, 'advertiser_application', None)
        if app:
            if app.registration_certificate and not app.registration_verified: unverified.append("Registration")
            if app.gst_certificate and not app.gst_verified: unverified.append("GST Certificate")
            if app.pan_card and not app.pan_verified: unverified.append("PAN Card")
            if app.bank_details and not app.bank_verified: unverified.append("Bank Details")

    if unverified:
        from django.contrib import messages
        messages.warning(request, f"Action blocked: Complete document verification ({', '.join(unverified)}) before approving the application.")
        return redirect(request.META.get('HTTP_REFERER', 'admin_panel_applications'))

    user.approval_status = "approved"
    user.save()

    # Update app status
    if user.role == "journalist":
        try:
            app = user.journalist_application
            app.status = "approved"
            app.save()
        except: pass
    elif user.role == "advertiser":
        try:
            app = user.advertiser_application
            app.status = "approved"
            app.save()
        except: pass

    from urllib.parse import urlencode

    redirect_url = reverse("admin_panel_applications")
    params = {}
    if request.GET.get("q"):
        params["q"] = request.GET.get("q")
    if request.GET.get("tab"):
        params["tab"] = request.GET.get("tab")

    if params:
        redirect_url = f"{redirect_url}?{urlencode(params)}"
    return redirect(redirect_url)


def adminPanelApplicationsReject(request,id):
    user = get_object_or_404(User,id=id)
    user.approval_status = "rejected"
    
    if user.role == "journalist" and hasattr(user, 'journalist_application'):
        app = user.journalist_application
        app.status = "rejected"
        reason = request.GET.get("reason", "").strip()
        if reason:
            app.rejection_reason = reason
        app.save()
    elif user.role == "advertiser" and hasattr(user, 'advertiser_application'):
        app = user.advertiser_application
        app.status = "rejected"
        reason = request.GET.get("reason", "").strip()
        if reason:
            app.rejection_reason = reason
        app.save()

    user.save()
    from urllib.parse import urlencode

    redirect_url = reverse("admin_panel_applications")
    params = {}
    if request.GET.get("q"):
        params["q"] = request.GET.get("q")
    if request.GET.get("tab"):
        params["tab"] = request.GET.get("tab")

    if params:
        redirect_url = f"{redirect_url}?{urlencode(params)}"
    return redirect(redirect_url)


def adminPanelJournalistsView(request):
    query = request.GET.get("q")


    if query:
        users = User.objects.filter(role__in=["journalist"])
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        users = users.order_by("-id")
    else:
        users = User.objects.filter(role__in=['journalist']).order_by('id')

    return render(request, 'adminPanel/adminPanelJournalists.html', {'users':users})

def adminPanelAdvertisersView(request):
    query = request.GET.get("q")


    if query:
        users = User.objects.filter(role__in=["advertiser"])
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        users = users.order_by("-id")
    else:
        users = User.objects.filter(role__in=['advertiser']).order_by('id')

    return render(request, 'adminPanel/adminPanelAdvertisers.html', {'users':users})


def adminPanelReadersView(request):
    query = request.GET.get("q")


    if query:
        users = User.objects.filter(role__in=["reader"])
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        users = users.order_by("-id")
    else:
        users = User.objects.filter(role__in=['reader']).order_by('id')

    return render(request, 'adminPanel/adminPanelReaders.html', {'users':users})


@role_required(allowed_roles=["admin"])
def adminPanelArticlesView(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all").strip()

    base_qs = News_article.objects.select_related("author_id", "category_id")

    if q:
        base_qs = base_qs.filter(
            Q(title__icontains=q) |
            Q(author_id__first_name__icontains=q) |
            Q(author_id__last_name__icontains=q)
        )

    stats_qs = base_qs
    stats = {
        "total": stats_qs.count(),
        "approved": stats_qs.filter(status="approved").count(),
        "pending": stats_qs.filter(status="pending").count(),
        "reported": stats_qs.filter(article_reports__isnull=False).distinct().count(),
        "rejected": stats_qs.filter(status="rejected").count(),
    }

    articles_qs = base_qs
    if status == "reported":
        articles_qs = articles_qs.filter(article_reports__isnull=False).distinct()
    elif status != "all":
        articles_qs = articles_qs.filter(status=status)

    articles_list = articles_qs.order_by("-created_at")
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(articles_list, 10)  # 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "adminPanel/adminPanelArticles.html",
        {
            "articles": page_obj,
            "stats": stats,
            "current": {"q": q, "status": status},
        },
    )


@role_required(allowed_roles=["admin"])
def adminPanelArticleApproveView(request, id):
    article = get_object_or_404(News_article, id=id)
    article.status = "approved"
    article.published_at = timezone.now()
    article.rejection_reason = None
    article.save()
    return redirect("admin_panel_articles")


@role_required(allowed_roles=["admin"])
def adminPanelArticleRejectView(request, id):
    article = get_object_or_404(News_article, id=id)
    article.status = "rejected"
    article.published_at = None
    
    reason = request.GET.get("reason", "").strip()
    if reason:
        article.rejection_reason = reason
    elif not article.rejection_reason:
        article.rejection_reason = "Rejected by admin."
        
    article.save()
    return redirect("admin_panel_articles")


@role_required(allowed_roles=["admin"])
def adminPanelArticleDeleteView(request, id):
    News_article.objects.filter(id=id).delete()
    return redirect("admin_panel_articles")


@role_required(allowed_roles=["admin"])
def adminPanelCommentsView(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all").strip()

    base_qs = Comment.objects.select_related("user", "article")

    if q:
        base_qs = base_qs.filter(
            Q(comment_text__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(article__title__icontains=q)
        )

    stats_qs = base_qs
    today = timezone.localdate()
    stats = {
        "total": stats_qs.count(),
        "active": stats_qs.filter(status="Active").count(),
        "reported": stats_qs.filter(comment_reports__isnull=False).distinct().count(),
        "blocked": stats_qs.filter(status="Blocked").count(),
        "today": stats_qs.filter(created_at__date=today).count(),
    }

    comments_qs = base_qs
    if status == "reported":
        comments_qs = comments_qs.filter(comment_reports__isnull=False).distinct()
    elif status != "all":
        comments_qs = comments_qs.filter(status=status)

    comments = comments_qs.order_by("-created_at")

    return render(
        request,
        "adminPanel/adminPanelComments.html",
        {
            "comments": comments,
            "stats": stats,
            "current": {"q": q, "status": status},
        },
    )


@role_required(allowed_roles=["admin"])
def adminPanelCommentBlockView(request, id):
    comment = get_object_or_404(Comment, id=id)
    comment.status = "Blocked"
    comment.save()
    return redirect("admin_panel_comments")


@role_required(allowed_roles=["admin"])
def adminPanelCommentUnblockView(request, id):
    comment = get_object_or_404(Comment, id=id)
    comment.status = "Active"
    comment.save()
    return redirect("admin_panel_comments")


@role_required(allowed_roles=["admin"])
def adminPanelCommentDeleteView(request, id):
    Comment.objects.filter(id=id).delete()
    return redirect("admin_panel_comments")


@role_required(allowed_roles=["admin"])
def adminPanelUserBlockView(request, id):
    user = get_object_or_404(User, id=id)
    user.account_status = 'blocked'
    user.is_active = False
    user.save()
    messages.success(request, f"User {user.email} has been blocked.")
    return redirect("admin_panel_comments")


# @login_required(login_url='login')
# @role_required(allowed_roles=["reader"])
def readerDashboardView(request):
    return redirect('reader_saved_articles')

# @login_required
def readerSavedArticlesView(request):
    search = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "newest")
    
    # Base QuerySet for this user
    base_qs = SavedArticle.objects.filter(user=request.user).select_related(
        'article', 
        'article__category_id', 
        'article__city_id'
    )
    
    # Calculate stats BEFORE search
    total_count = base_qs.count()
    
    # Apply search
    if search:
        base_qs = base_qs.filter(article__title__icontains=search)
        
    # Apply sorting
    if sort == "oldest":
        base_qs = base_qs.order_by("saved_at")
    elif sort == "title":
        base_qs = base_qs.order_by("article__title")
    else: # newest
        base_qs = base_qs.order_by("-saved_at")
        
    saved_articles = base_qs.prefetch_related('article__media')
    
    context = {
        "saved_articles": saved_articles,
        "stats": {
            "total": total_count,
        },
        "current": {
            "q": search,
            "sort": sort,
        },
    }
    return render(request, "reader/readerSavedArticles.html", context)


def readerUnsaveArticleView(request, article_id):
    if request.user.is_authenticated:
        SavedArticle.objects.filter(user=request.user, article_id=article_id).delete()
        messages.success(request, "Article removed from your saved items.")
    return redirect('reader_saved_articles')


def readerProfileView(request):
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
        return redirect("reader_profile")

    states = State.objects.all()
    cities = City.objects.all()
    
    return render(request, "reader/readerProfile.html", {
        "states": states,
        "cities": cities,
        "profile": profile,
    })


def readerGeneralView(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "update_notifications" in request.POST:
            profile.email_notifications = request.POST.get("email_notifications") == "on"
            profile.breaking_news_alerts = request.POST.get("breaking_news_alerts") == "on"
            profile.weekly_newsletter = request.POST.get("weekly_newsletter") == "on"
            profile.article_recommendations = request.POST.get("article_recommendations") == "on"
            profile.save()
            messages.success(request, "Notification preferences updated successfully.")
            return redirect("reader_general")
            
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
            return redirect("reader_general")
            
        elif "delete_account" in request.POST:
            user = request.user
            user.delete()
            return redirect("/")  # Redirect to home/login after deletion

    return render(request, "reader/readerGeneral.html", {"profile": profile})


def saveArticleView(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Please log in to save articles.'}, status=403)
    
    article = get_object_or_404(News_article, id=article_id)
    saved_exists = SavedArticle.objects.filter(user=request.user, article=article).exists()
    
    if saved_exists:
        SavedArticle.objects.filter(user=request.user, article=article).delete()
        return JsonResponse({'message': 'Article removed from saved items.'})
    
    SavedArticle.objects.create(user=request.user, article=article)
    return JsonResponse({'message': 'Article saved successfully!'})


def reportArticleView(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Please log in to report articles.'}, status=403)
    
    if request.method == 'POST':
        article = get_object_or_404(News_article, id=article_id)
        description = request.POST.get('description', '')
        
        if not description:
            return JsonResponse({'message': 'Reporting reason is required.'}, status=400)
            
        CitizenReport.objects.create(
            user=request.user,
            article=article,
            title=f"Article Report: {article.title[:50]}",
            description=description,
            state=article.city_id.state_id,
            city=article.city_id
        )
        return JsonResponse({'message': 'Thank you. The article has been reported and will be reviewed.'})
    
    return JsonResponse({'message': 'Invalid request method.'}, status=405)


def reportCommentView(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Please log in to report comments.'}, status=403)
    
    if request.method == 'POST':
        from news.models import Comment
        from reports.models import CommentReport
        comment = get_object_or_404(Comment, id=comment_id)
        reason = request.POST.get('description', '').strip()
        
        if not reason:
            return JsonResponse({'message': 'Reporting reason is required.'}, status=400)
            
        CommentReport.objects.create(
            user=request.user,
            comment=comment,
            reason=reason
        )
        return JsonResponse({'message': 'Thank you. The comment has been reported and will be reviewed.'})
    
    return JsonResponse({'message': 'Invalid request method.'}, status=405)


def simplifiedPasswordResetView(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not email or not password or not confirm_password:
            return render(request, 'auth/password_reset_form.html', {
                'error': 'All fields are required.',
                'email': email
            })

        if password != confirm_password:
            return render(request, 'auth/password_reset_form.html', {
                'error': 'Passwords do not match.',
                'email': email
            })

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            return render(request, 'auth/password_reset_complete.html')
        except User.DoesNotExist:
            return render(request, 'auth/password_reset_form.html', {
                'error': 'No account found with this email.',
                'email': email
            })
    
    return render(request, 'auth/password_reset_form.html')

# @login_required(login_url='login')
def addCommentView(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(News_article, id=article_id)
        comment_text = request.POST.get('comment_text', '').strip()
        
        if comment_text:
            Comment.objects.create(
                article=article,
                user=request.user,
                comment_text=comment_text
            )
        
        return redirect('article_detail', slug=article.slug)
    
    return redirect('home')

# @login_required(login_url='login')
def journalistApplicationView(request):
    if request.user.role != 'journalist' or request.user.approval_status == 'approved':
        return redirect('home')
        
    if request.method != 'POST' and hasattr(request.user, 'journalist_application') and not request.GET.get('edit'):
        return redirect('journalist_pending')
        
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        from .models import JournalistApplication

        app, _ = JournalistApplication.objects.get_or_create(user=user)

        # Map existing template field names to form/model field names.
        post_data = request.POST.copy()
        post_data["first_name"] = request.POST.get("firstName", "")
        post_data["last_name"] = request.POST.get("lastName", "")
        post_data["remove_portfolio"] = request.POST.get("remove_portfolio") == "true"
        post_data["remove_presscard"] = request.POST.get("remove_presscard") == "true"
        post_data["remove_recommendation"] = request.POST.get("remove_recommendation") == "true"

        user_form = JournalistIdentityForm(post_data, instance=user)
        profile_form = JournalistProfileLocationForm(post_data, instance=profile)
        app_form = JournalistApplicationDocumentsForm(post_data, request.FILES, instance=app)

        if user_form.is_valid() and profile_form.is_valid() and app_form.is_valid():
            user_form.save()
            profile_form.save()

            updated_app = app_form.save(commit=False)

            if app_form.cleaned_data.get("remove_portfolio"):
                updated_app.portfolio_file = None
                updated_app.portfolio_verified = False
            elif request.FILES.get("portfolio_file"):
                updated_app.portfolio_verified = False

            if app_form.cleaned_data.get("remove_presscard"):
                updated_app.press_card_file = None
                updated_app.press_card_verified = False
            elif request.FILES.get("press_card_file"):
                updated_app.press_card_verified = False

            if app_form.cleaned_data.get("remove_recommendation"):
                updated_app.recommendation_file = None
                updated_app.recommendation_verified = False
            elif request.FILES.get("recommendation_file"):
                updated_app.recommendation_verified = False

            if request.FILES.get("aadhaar_file"):
                updated_app.aadhaar_verified = False

            updated_app.status = "pending"
            updated_app.submitted_at = timezone.now()
            updated_app.save()

            messages.success(request, 'Application Submitted Successfully!')
            return redirect('journalist_pending')

        messages.error(request, "Please fix the form errors and submit again.")
        return redirect("journalist_application")
        
    states = State.objects.all()
    cities = City.objects.all()
    return render(request, 'journalist/journalist_application.html', {'states': states, 'cities': cities})

# @login_required(login_url='login')
def journalistPendingView(request):
    if request.user.role != 'journalist' or request.user.approval_status == 'approved':
        return redirect('home')
        
    if not hasattr(request.user, 'journalist_application'):
        return redirect('journalist_application')
        
    return render(request, 'journalist/journalist_pending.html')

# @login_required(login_url='login')
def journalistWithdrawView(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.role == 'journalist':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your application has been withdrawn and account deleted.')
    return redirect('home')

@login_required
def adminPanelDocumentActionView(request, user_id, doc_slug, action):
    if request.user.role != 'admin':
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    from ads.models import AdvertiserApplication
    from .models import JournalistApplication
    
    app = None
    if user.role == "journalist":
        app = JournalistApplication.objects.filter(user=user).first()
    elif user.role == "advertiser":
        app = AdvertiserApplication.objects.filter(user=user).first()
    
    if not app:
        return JsonResponse({"error": "Application not found"}, status=404)
    
    # Map slug to field
    field_map = {
        "aadhaar_id": "aadhaar_verified",
        "aadhaar_card": "aadhaar_verified",
        "portfolio": "portfolio_verified",
        "press_card": "press_card_verified",
        "recommendation": "recommendation_verified",
        "recommendation_letter": "recommendation_verified",
        "registration": "registration_verified",
        "registration_certificate": "registration_verified",
        "gst_certificate": "gst_verified",
        "pan_card": "pan_verified",
        "bank_details": "bank_verified",
    }
    
    field_name = field_map.get(doc_slug)
    if not field_name:
        return JsonResponse({"error": f"Invalid document slug: {doc_slug}"}, status=400)
    
    if action == "approve":
        setattr(app, field_name, True)
        app.save()
        return JsonResponse({"status": "success", "message": f"{doc_slug} approved"})
    elif action == "reject":
        reason = request.POST.get("reason", "Incomplete/Invalid document")
        setattr(app, field_name, False)
        # Update overall rejection reason too
        existing_reason = app.rejection_reason or ""
        new_reason_entry = f"{doc_slug.replace('_', ' ').capitalize()}: {reason}"
        if new_reason_entry not in existing_reason:
           app.rejection_reason = f"{existing_reason}\n{new_reason_entry}".strip()
        app.save()
        return JsonResponse({"status": "success", "message": f"{doc_slug} rejected"})
    
    return JsonResponse({"error": "Invalid action"}, status=400)
