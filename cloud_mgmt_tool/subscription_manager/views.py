from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Subscription
from .serializers import SubscriptionSerializer
from .cloud_api import CloudAPI
from .payment_api import PaymentAPI
from .auth_api import AuthAPI
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def user_profile(request):
    return render(request, 'subscription_manager/user_profile.html')



@login_required
def export_user_data(request):
    # Replace this with actual subscription data logic
    user = request.user
    subscriptions = [
        {"name": "AWS", "status": "Active", "cost": "$120"},
        {"name": "Azure", "status": "Inactive", "cost": "$0"},
    ]

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_data.csv"'

    writer = csv.writer(response)
    writer.writerow(["Username", "Email", "Last Login"])
    writer.writerow([user.username, user.email, user.last_login])

    writer.writerow([])
    writer.writerow(["Subscription Name", "Status", "Cost"])

    for sub in subscriptions:
        writer.writerow([sub["name"], sub["status"], sub["cost"]])

    return response

# ✅ Dashboard view (with context data)
def dashboard(request):
    context = {
        "active_subscriptions": [
            {"name": "AWS EC2", "status": "Active"},
            {"name": "Azure VM", "status": "Active"},
            {"name": "GCP Compute", "status": "Inactive"},
        ],
        "cost_breakdown": {
            "total": 120.50,
            "last_month": 110.00,
        },
        "activity_logs": [
            "User logged in",
            "Added new subscription: AWS EC2",
            "Updated billing details",
        ],
    }
    return render(request, 'subscription_manager/dashboard.html', context)

# ✅ Home view for root '/'
def home(request):
    return render(request, 'home.html')

# ✅ Subscription list view
def subscription_list(request):
    subscriptions = Subscription.objects.all()
    return render(request, 'subscriptions/subscription_list.html', {'subscriptions': subscriptions})

# ✅ User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# ✅ DRF API view to list subscriptions as JSON
@api_view(['GET'])
def subscription_list_api(request):
    subscriptions = Subscription.objects.all()
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)

# ✅ Cloud API integration example
def list_cloud_resources(request, provider):
    api = CloudAPI(provider)
    return JsonResponse({"message": api.list_resources()})

# ✅ Subscription creation example via payment API
def create_subscription(request, provider, email):
    payment_api = PaymentAPI(provider)
    return JsonResponse({"message": payment_api.create_subscription(email)})

# ✅ Auth provider login redirection
def login_redirect(request, provider):
    auth_api = AuthAPI(provider)
    return JsonResponse({"message": auth_api.login_url()})

# ✅ Custom login view using admin-style login template
class AdminStyleLoginView(LoginView):
    template_name = 'admin/login.html'
