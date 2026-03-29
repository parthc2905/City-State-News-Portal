from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm, UserLoginForm, CommentForm
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, F
from news.models import News_article, SavedArticle, Comment
from reports.models import CitizenReport
from django.http import JsonResponse
from .models import Profile
from location.models import State, City
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
def articleDetailView(request, slug):
    # Fetch published article only
    article = get_object_or_404(
        News_article.objects.prefetch_related('media').select_related(
            'author_id', 'category_id', 'city_id__state_id'
        ),
        slug=slug,
        status='approved',
    )

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
                    return redirect('admin_dashboard') # Replace with your admin dashboard URL name
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

# @login_required(login_url='login')
# @role_required(allowed_roles=["admin"])
def adminPanelDashboardView(request):
    return redirect('admin_panel_applications')


def adminPanelApplicationsView(request):
    query = request.GET.get("q")


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



    return render(request, 'adminPanel/adminPanelApplications.html', {'users':users})


def adminPanelApplicationsApproval(request,id):
    user = get_object_or_404(User,id=id)
    user.approval_status = "approved"
    user.save()
    return redirect('admin_panel_applications')


def adminPanelApplicationsReject(request,id):
    user = get_object_or_404(User,id=id)
    user.approval_status = "rejected"
    user.save()
    return redirect('admin_panel_applications')


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
        
    if request.method != 'POST' and hasattr(request.user, 'journalist_application'):
        return redirect('journalist_pending')
        
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('firstName', user.first_name)
        user.last_name = request.POST.get('lastName', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        
        state_id = request.POST.get('state')
        city_id = request.POST.get('city')
        if state_id:
            profile.state_id = state_id
        if city_id:
            profile.city_id = city_id
            
        profile.save()
        
        from .models import JournalistApplication
        JournalistApplication.objects.filter(user=user).delete()
        JournalistApplication.objects.create(
            user=user,
            aadhaar_file=request.FILES.get('aadhaar_file'),
            portfolio_file=request.FILES.get('portfolio_file'),
            press_card_file=request.FILES.get('press_card_file'),
            recommendation_file=request.FILES.get('recommendation_file')
        )
        
        messages.success(request, 'Application Submitted Successfully!')
        return redirect('journalist_pending')
        
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
