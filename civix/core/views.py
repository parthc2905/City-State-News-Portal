from django.shortcuts import render, redirect
from .forms import UserSignupForm

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