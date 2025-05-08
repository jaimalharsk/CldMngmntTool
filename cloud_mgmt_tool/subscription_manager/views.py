from django.contrib.auth import login
from .forms import CustomUserCreationForm, BudgetForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Subscription, CloudAccount, Budget
from .serializers import SubscriptionSerializer
from .cloud_api import CloudAPI
from .payment_api import PaymentAPI
from .auth_api import AuthAPI
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import csv
from django.shortcuts import render
from .models import Budget

# Define the set_budget view
def set_budget(request):
    if request.method == "POST":
        # Logic for handling POST request to set a budget
        amount = request.POST.get('amount')
        user = request.user
        Budget.objects.create(user=user, amount=amount)
        # Redirect to another page or return a response
    return render(request, 'set_budget.html')  # Return the set_budget template

# Full Dashboard View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Subscription, Budget
from .forms import BudgetForm

@login_required
def dashboard(request):
    budget_form = BudgetForm()

    # Handling the POST request to set a new budget
    if request.method == 'POST' and 'set_budget' in request.POST:
        budget_form = BudgetForm(request.POST)
        if budget_form.is_valid():
            cd = budget_form.cleaned_data
            Budget.objects.create(
                user=request.user,
                cloud_provider=cd['cloud_provider'],
                monthly_budget=cd['monthly_budget'],
                service_name=cd.get('service_name'),
                alert_threshold=cd['alert_threshold'],
            )
            messages.success(request, "Budget set successfully!")
            return redirect('dashboard')

    # Get active subscriptions and user budgets
    active_subs = Subscription.objects.filter(status='Active')
    all_subs = Subscription.objects.all()
    user_budgets = Budget.objects.filter(user=request.user)

    # Initialize the services list to match budgets to services
    services = []
    for sub in active_subs:
        # Get the matched budget for each active subscription
        matched_budget = user_budgets.filter(service_name=sub.service_name).first()

        # If a matched budget exists, get the monthly budget and threshold; else, set to 0 and 80
        budget_amount = matched_budget.monthly_budget if matched_budget else 0
        threshold = matched_budget.alert_threshold if matched_budget else 80

        # Calculate usage percent based on price and budget amount
        usage_percent = round((sub.price / budget_amount) * 100, 2) if budget_amount else 0

        # Append the service details to the services list
        services.append({
            'name': sub.service_name,
            'usage_percent': usage_percent,
            'cost': sub.price,
            'threshold': threshold,
            'budget': budget_amount
        })

    # Calculate the total monthly cost of active subscriptions
    monthly_cost = sum(sub.price for sub in active_subs if sub.price)
    # Count the number of subscriptions that are pending
    pending_alerts = all_subs.filter(status='Pending').count()

    # Get the total budget limit (you can sum this dynamically or use a fixed value)
    budget_limit = sum(user_budgets.values_list('monthly_budget', flat=True))

    # Usage and Billing chart data
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

    # Render the dashboard with all the required context
    return render(request, 'subscription_manager/dashboard.html', {
        'active_subscriptions': active_subs,
        'subscriptions': all_subs,
        'monthly_cost': monthly_cost,
        'pending_alerts': pending_alerts,
        'budget_limit': budget_limit,
        'usage_chart': usage_chart,
        'billing_chart': billing_chart,
        'budget_form': budget_form,
        'budgets': user_budgets,
        'services': services,  # ⬅️ This powers your new unified table
    })


# Cloud Account Connection
@login_required
def connect_cloud(request):
    if request.method == 'POST':
        provider = request.POST.get('provider')
        CloudAccount.objects.create(
            user=request.user,
            provider=provider,
            access_key=request.POST.get('aws_access_key'),
            secret_key=request.POST.get('aws_secret_key'),
            role_arn=request.POST.get('aws_iam_arn'),
            project_id=request.POST.get('gcp_project_id'),
            subscription_id=request.POST.get('azure_subscription_id'),
            tenant_id=request.POST.get('azure_tenant_id'),
        )
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request method."})

# User Profile View
@login_required
def user_profile(request):
    return render(request, 'subscription_manager/user_profile.html')

# Export User Data to CSV
@login_required
def export_user_data(request):
    user = request.user
    subscriptions = [
        {"name": "AWS", "status": "Active", "cost": "$120"},
        {"name": "Azure", "status": "Inactive", "cost": "$0"},
    ]

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

# Home View
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


from django.shortcuts import render
from django.utils import timezone

from django.contrib.auth import login
from .forms import CustomUserCreationForm, BudgetForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Subscription, CloudAccount, Budget
from .serializers import SubscriptionSerializer
from .cloud_api import CloudAPI
from .payment_api import PaymentAPI
from .auth_api import AuthAPI
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import csv
from django.shortcuts import render
from .models import Budget

# Define the set_budget view
def set_budget(request):
    if request.method == "POST":
        provider = request.POST.get('provider')
        amount = request.POST.get('budget')
        threshold = request.POST.get('threshold')
        user = request.user

        # Validate fields
        if not provider or not amount:
            messages.error(request, "Cloud provider and budget are required.")
            return redirect('dashboard')

        try:
            amount = float(amount)
        except ValueError:
            messages.error(request, "Budget must be a valid number.")
            return redirect('dashboard')

        try:
            threshold = int(threshold) if threshold else 80  # Default to 80 if empty
            if not (50 <= threshold <= 100):
                raise ValueError
        except ValueError:
            messages.error(request, "Threshold must be a number between 50 and 100.")
            return redirect('dashboard')

        # Save the budget
        Budget.objects.create(
            user=user,
            provider=provider,
            amount=amount,
            threshold=threshold
        )

        messages.success(request, f"{provider.upper()} budget of ₹{amount} set with {threshold}% threshold.")
        return redirect('dashboard')

    return redirect('dashboard')

# Full Dashboard View
@login_required
def dashboard(request):
    budget_form = BudgetForm()
    if request.method == 'POST' and 'set_budget' in request.POST:
        budget_form = BudgetForm(request.POST)
        if budget_form.is_valid():
            cd = budget_form.cleaned_data
            Budget.objects.create(
                user=request.user,
                cloud_provider=cd['cloud_provider'],
                monthly_budget=cd['monthly_budget'],
                service_name=cd.get('service_name'),
                alert_threshold=cd['alert_threshold'],
            )
            messages.success(request, "Budget set successfully!")
            return redirect('dashboard')

    active_subs = Subscription.objects.filter(status='Active')
    all_subs = Subscription.objects.all()
    user_budgets = Budget.objects.filter(user=request.user)

    monthly_cost = sum(sub.price for sub in active_subs if sub.price)
    pending_alerts = all_subs.filter(status='Pending').count()
    budget_limit = 500  # Optional static value or sum of user_budgets

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
        'budget_form': budget_form,
        'budgets': user_budgets,
    })

# Cloud Account Connection
@login_required
def connect_cloud(request):
    if request.method == 'POST':
        provider = request.POST.get('provider')
        CloudAccount.objects.create(
            user=request.user,
            provider=provider,
            access_key=request.POST.get('aws_access_key'),
            secret_key=request.POST.get('aws_secret_key'),
            role_arn=request.POST.get('aws_iam_arn'),
            project_id=request.POST.get('gcp_project_id'),
            subscription_id=request.POST.get('azure_subscription_id'),
            tenant_id=request.POST.get('azure_tenant_id'),
        )
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request method."})

# User Profile View
@login_required
def user_profile(request):
    return render(request, 'subscription_manager/user_profile.html')

# Export User Data to CSV
@login_required
def export_user_data(request):
    user = request.user
    subscriptions = [
        {"name": "AWS", "status": "Active", "cost": "$120"},
        {"name": "Azure", "status": "Inactive", "cost": "$0"},
    ]

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

# Home View
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


from django.shortcuts import render
from django.utils import timezone

# def dashboard_view(request):
#     # Dummy service data (simulate AWS, Azure, GCP usage)
#     services = [
#         {'name': 'AWS EC2', 'usage': 75, 'cost': 120, 'status': 'Running'},
#         {'name': 'Azure Blob', 'usage': 55, 'cost': 80, 'status': 'Active'},
#         {'name': 'GCP Compute', 'usage': 30, 'cost': 60, 'status': 'Idle'},
#     ]
#
#     # Dummy budget info
#     budgets = [
#         {'amount': 300, 'date_set': timezone.now()}
#     ]
#
#     # Calculate monthly cost and budget limit safely
#     monthly_cost = sum(service['cost'] for service in services)
#     budget_limit = budgets[0]['amount'] if budgets else 0
#
#     # Pass everything to the template
#     context = {
#         'services': services,
#         'budgets': budgets,
#         'monthly_cost': monthly_cost,
#         'budget_limit': budget_limit,
#     }
#
#     return render(request, 'dashboard.html', context)



