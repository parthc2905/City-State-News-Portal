from django.shortcuts import render,redirect
from .models import News_article, ArticleMedia, Category
from location.models import City
from .forms import ArticleMediaForm, ArticleWriteForm

# Create your views here.
def journalistDashboardView(request):
    return redirect('journalist_write_article')


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
    return render(request, 'journalist/journalistWriteArticle.html',{"articleForm" : article , 'articleMedia' : articleMedia})


def journalistMyArticlesView(request):
    if request.method == "POST":
        pass
    else:
        pass
    return render(request, 'journalist/journalistMyArticles.html')

def journalistProfileView(request):
    if request.method == "POST":
        pass
    else:
        pass
    return render(request, 'journalist/journalistProfile.html')

def journalistGeneralView(request):
    if request.method == "POST":
        pass
    else:
        pass
    return render(request, 'journalist/journalistGeneral.html')