from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from rest_framework.decorators import api_view
from rest_framework.response import Response

import csv
from .forms import CustomUserCreationForm, BudgetForm, SubscriptionForm
from .models import Subscription, CloudAccount, Budget,CloudAccountUsage
from .serializers import SubscriptionSerializer
from .cloud_api import CloudAPI
from .payment_api import PaymentAPI
from .auth_api import AuthAPI

User = get_user_model()

# ========== Registration ==========
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# ========== Custom Login ==========
class AdminStyleLoginView(LoginView):
    template_name = 'admin/login.html'


# ========== Home ==========
def home(request):
    return render(request, 'home.html')


# ========== Dashboard ==========
@login_required
def dashboard(request):
    target_user = request.user  # ✅ Use the actual logged-in user

    budget_form = BudgetForm()
    subscription_form = SubscriptionForm()

    if request.method == 'POST':
        if 'set_budget' in request.POST:
            budget_form = BudgetForm(request.POST)
            if budget_form.is_valid():
                budget = budget_form.save(commit=False)
                budget.user = target_user
                budget.save()
                messages.success(request, "Budget set successfully!")
                return redirect('dashboard')

        elif 'add_subscription' in request.POST:
            subscription_form = SubscriptionForm(request.POST)
            if subscription_form.is_valid():
                subscription = subscription_form.save(commit=False)
                subscription.user = target_user
                subscription.save()
                messages.success(request, "Subscription added!")
                return redirect('dashboard')

    # Fetch budgets and subscriptions for the logged-in user
    user_budgets = Budget.objects.filter(user=target_user)
    user_subs = Subscription.objects.filter(user=target_user)

    # Build lookup maps for budgets to avoid N+1 queries
    budget_map = {budget.cloud_provider.lower(): budget for budget in user_budgets}

    services = []
    for sub in user_subs.filter(status='active'):
        # Fetch the specific budget for each subscription
        budget = budget_map.get(sub.service_name.lower()) or budget_map.get('all')  # Fallback to default budget ('all')

        budget_amount = budget.monthly_budget if budget else 0
        threshold = budget.alert_threshold if budget else 80

        # Calculate usage percentage
        usage_percent = round((sub.price / budget_amount) * 100, 2) if budget_amount else 0

        services.append({
            'name': sub.service_name,
            'cost': sub.price,
            'budget': budget_amount,
            'threshold': threshold,
            'usage_percent': usage_percent,
        })

    # Additional data for charts and summaries
    monthly_cost = sum(sub.price for sub in user_subs if sub.price)
    pending_alerts = user_subs.filter(status='Pending').count()
    budget_limit = sum(user_budgets.values_list('monthly_budget', flat=True))

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
    print(services)
    return render(request, 'subscription_manager/dashboard.html', {
        'active_subscriptions': user_subs.filter(status='Active'),
        'subscriptions': user_subs,
        'monthly_cost': monthly_cost,
        'pending_alerts': pending_alerts,
        'budget_limit': budget_limit,
        'usage_chart': usage_chart,
        'billing_chart': billing_chart,
        'budget_form': budget_form,
        'subscription_form': subscription_form,
        'budgets': user_budgets,
        'services': services,
    })




# ========== Fallback Budget Endpoint ==========
@login_required
def set_budget(request):
    if request.method == "POST":
        provider = request.POST.get('provider')
        monthly_budget = request.POST.get('budget')
        alert_threshold = request.POST.get('threshold')
        user = request.user

        if not provider or not monthly_budget:
            messages.error(request, "Cloud provider and budget are required.")
            return redirect('dashboard')

        try:
            monthly_budget = float(monthly_budget)
        except ValueError:
            messages.error(request, "Budget must be a valid number.")
            return redirect('dashboard')

        try:
            alert_threshold = int(alert_threshold) if alert_threshold else 80
            if not (50 <= alert_threshold <= 100):
                raise ValueError
        except ValueError:
            messages.error(request, "Threshold must be between 50 and 100.")
            return redirect('dashboard')

        Budget.objects.create(
            user=user,
            cloud_provider=provider,
            monthly_budget=monthly_budget,
            alert_threshold=alert_threshold
        )

        messages.success(request, f"{provider.upper()} budget of ₹{monthly_budget} set with {alert_threshold}% threshold.")
        return redirect('dashboard')

    return redirect('dashboard')


# ========== Cloud Account ==========
def connect_cloud(request):
    if request.method == 'POST':
        provider = request.POST.get('provider')

        # AWS specific validation
        if provider == 'aws':
            aws_access_key = request.POST.get('aws_access_key')
            aws_secret_key = request.POST.get('aws_secret_key')
            aws_iam_arn = request.POST.get('aws_iam_arn')

            # Validate AWS credentials by trying to access AWS STS service
            try:
                sts_client = boto3.client(
                    'sts',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
                # Try to get the caller identity to validate the connection
                sts_client.get_caller_identity()

                # If successful, save the CloudAccount to DB
                CloudAccount.objects.create(
                    user=request.user,
                    provider=provider,
                    access_key=aws_access_key,
                    secret_key=aws_secret_key,
                    role_arn=aws_iam_arn,
                )
                return JsonResponse({"success": True, "message": "AWS account connected successfully!"})

            except NoCredentialsError:
                return JsonResponse({"success": False, "error": "AWS credentials are missing or invalid."})
            except ClientError as e:
                return JsonResponse({"success": False, "error": f"Failed to connect to AWS: {str(e)}"})

        # Add future handling for GCP or Azure here (could be similar steps)
        elif provider == 'gcp':
            project_id = request.POST.get('gcp_project_id')
            # Example validation for GCP (could add actual GCP SDK calls)
            if project_id:
                # Save to DB if successful
                CloudAccount.objects.create(
                    user=request.user,
                    provider=provider,
                    project_id=project_id
                )
                return JsonResponse({"success": True, "message": "GCP account connected successfully!"})
            else:
                return JsonResponse({"success": False, "error": "Invalid GCP project ID."})

        elif provider == 'azure':
            subscription_id = request.POST.get('azure_subscription_id')
            tenant_id = request.POST.get('azure_tenant_id')
            # Example validation for Azure (could add actual Azure SDK calls)
            if subscription_id and tenant_id:
                # Save to DB if successful
                CloudAccount.objects.create(
                    user=request.user,
                    provider=provider,
                    subscription_id=subscription_id,
                    tenant_id=tenant_id
                )
                return JsonResponse({"success": True, "message": "Azure account connected successfully!"})
            else:
                return JsonResponse({"success": False, "error": "Invalid Azure credentials."})

        else:
            return JsonResponse({"success": False, "error": "Unsupported provider."})

    return JsonResponse({"success": False, "error": "Invalid request method."})


# ========== Profile ==========
@login_required
def user_profile(request):
    return render(request, 'subscription_manager/user_profile.html')


# ========== Export to CSV ==========
@login_required
def export_user_data(request):
    user = request.user
    subscriptions = Subscription.objects.filter(user=user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_data.csv"'

    writer = csv.writer(response)
    writer.writerow(["Username", "Email", "Last Login"])
    writer.writerow([user.username, user.email, user.last_login])

    writer.writerow([])
    writer.writerow(["Subscription Name", "Status", "Cost"])
    for sub in subscriptions:
        writer.writerow([sub.service_name, sub.status, sub.price])

    return response


# ========== Subscription List ==========
def subscription_list(request):
    subscriptions = Subscription.objects.all()
    return render(request, 'subscriptions/subscription_list.html', {'subscriptions': subscriptions})


@api_view(['GET'])
def subscription_list_api(request):
    subscriptions = Subscription.objects.all()
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)


# ========== Cloud API Integration ==========
def list_cloud_resources(request, provider):
    api = CloudAPI(provider)
    return JsonResponse({"message": api.list_resources()})


# ========== Subscription Creation (Mocked) ==========
def create_subscription(request, provider, email):
    payment_api = PaymentAPI(provider)
    return JsonResponse({"message": payment_api.create_subscription(email)})


# ========== Auth Redirect (Mocked) ==========
def login_redirect(request, provider):
    auth_api = AuthAPI(provider)
    return JsonResponse({"message": auth_api.login_url()})

def dashboard_ajax(request):
    cloud_accounts = CloudAccount.objects.filter(user=request.user)
    usage_data = CloudAccountUsage.objects.filter(cloud_account__in=cloud_accounts).order_by('-created_on')
    budgets = Budget.objects.filter(user=request.user)

    # Build lookup maps to avoid N+1 queries
    usage_map = {}
    for usage in usage_data:
        if usage.cloud_account_id not in usage_map:
            usage_map[usage.cloud_account_id] = usage  # use the latest one only

    budget_map = {budget.cloud_provider: budget for budget in budgets}

    cloud_data = []
    for account in cloud_accounts:
        usage = usage_map.get(account.id)
        budget = budget_map.get(account.provider)

        cloud_data.append({
            'account': {'provider': account.provider},
            'usage': {'total_cost': usage.total_cost if usage else 0},
            'budget': {'monthly_budget': budget.monthly_budget if budget else 0},
        })

    return JsonResponse({'success': True, 'cloud_data': cloud_data})