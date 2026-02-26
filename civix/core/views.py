from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserSignupForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import role_required

# signup view for user registration
def userSignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # for now error will be shown
        else:
            return render(request,'core/signup.html',{'form':form})  
    else:
        form = UserSignupForm()
        return render(request, 'core/signup.html', {'form': form})


# login view for user authentication
def userLoginView(request):
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
                    return redirect('reader_dashboard') # Replace with your reader dashboard URL name
            else:
                return render(request,'core/login.html',{'form':form}) 
    else:
        form = UserLoginForm()
        return render(request, 'core/login.html', {'form': form})   


# @login_required(login_url='login')
@role_required(allowed_roles=["admin"])
def adminDashboardView(request):
    return render(request, 'core/admin/admin_dashboard.html')


# @login_required(login_url='login')
@role_required(allowed_roles=["reader"])
def readerDashboardView(request):
    return render(request, 'core/reader/reader_dashboard.html')