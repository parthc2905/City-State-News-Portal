from django.shortcuts import render

# Create your views here.
def pricing_view(request):
    return render(request, 'subscriptions/pricing.html')
