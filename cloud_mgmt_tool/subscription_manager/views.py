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
import csv
from django.http import HttpResponse

from chartjs import chart
from chartjs.views.lines import BaseLineChartView

import random



def generate_usage_chart():
    # Dummy data for example
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    data = [random.randint(50, 150) for _ in range(6)]  # Example: random usage data for the months

    chart = Chart(
        {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Usage (GB)',
                    'data': data,
                    'fill': False,
                    'borderColor': 'rgba(75,192,192,1)',
                    'tension': 0.1,
                }],
            },
            'options': {
                'scales': {
                    'y': {
                        'beginAtZero': True,
                    },
                },
            },
        }
    )
    return chart.render()


def generate_billing_chart():
    # Dummy data for example
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    data = [random.randint(100, 300) for _ in range(6)]  # Example: random billing data for the months

    chart = chart(
        {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Billing ($)',
                    'data': data,
                    'backgroundColor': 'rgba(255,99,132,0.2)',
                    'borderColor': 'rgba(255,99,132,1)',
                    'borderWidth': 1,
                }],
            },
            'options': {
                'scales': {
                    'y': {
                        'beginAtZero': True,
                    },
                },
            },
        }
    )
    return chart.render()


# Dashboard view
def dashboard(request):
    # Get data
    active_subs = Subscription.objects.filter(status='Active')
    all_subs = Subscription.objects.all()

    monthly_cost = sum(sub.price for sub in active_subs if sub.price)
    pending_alerts = all_subs.filter(status='Pending').count()
    budget_limit = 500  # Replace with user-specific logic if needed

    # Chart Data
    usage_chart = {
        'type': 'line',
        'data': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [{
                'label': 'Usage (hrs)',
                'data': [10, 14, 8, 12, 16],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1,
                'fill': True,
            }]
        }
    }

    billing_chart = {
        'type': 'bar',
        'data': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [{
                'label': 'Billing ($)',
                'data': [100, 120, 90, 150, 130],
                'backgroundColor': 'rgba(255, 99, 132, 0.5)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
            }]
        }
    }

    return render(request, 'subscription_manager/dashboard.html', {
        'active_subscriptions': active_subs,
        'subscriptions': all_subs,
        'monthly_cost': monthly_cost,
        'pending_alerts': pending_alerts,
        'budget_limit': budget_limit,
        'usage_chart': usage_chart,
        'billing_chart': billing_chart,
    })

# User Profile View
@login_required
def user_profile(request):
    return render(request, 'subscription_manager/user_profile.html')

# Export User Data to CSV
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

    writer.writerow([])  # Empty row for separation
    writer.writerow(["Subscription Name", "Status", "Cost"])

    for sub in subscriptions:
        writer.writerow([sub["name"], sub["status"], sub["cost"]])

    return response

# Home View for root '/'
def home(request):
    return render(request, 'home.html')

# Subscription List View
def subscription_list(request):
    subscriptions = Subscription.objects.all()
    return render(request, 'subscriptions/subscription_list.html', {'subscriptions': subscriptions})

# User Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

# DRF API View for Subscription List
@api_view(['GET'])
def subscription_list_api(request):
    subscriptions = Subscription.objects.all()
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)

# Cloud API Integration Example
def list_cloud_resources(request, provider):
    api = CloudAPI(provider)
    return JsonResponse({"message": api.list_resources()})

# Subscription Creation Example via Payment API
def create_subscription(request, provider, email):
    payment_api = PaymentAPI(provider)
    return JsonResponse({"message": payment_api.create_subscription(email)})

# Auth Provider Login Redirection
def login_redirect(request, provider):
    auth_api = AuthAPI(provider)
    return JsonResponse({"message": auth_api.login_url()})

# Custom Login View with Admin-style Login Template
class AdminStyleLoginView(LoginView):
    template_name = 'admin/login.html'
