from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm, UserLoginForm
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

def homePage(request):
    return render(request, 'base/base.html')

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
                    return redirect('home')
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
    return render(request, 'core/reader/reader_dashboard.html')

 