from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views
from .views import list_cloud_resources, create_subscription, login_redirect,dashboard_ajax, export_user_data_xlsx


urlpatterns = [
    # Auth and Registration
    path('accounts/', include('allauth.urls')),  # Google OAuth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('registration/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # User pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/ajax/', dashboard_ajax, name='dashboard_ajax'),
    path('profile/', views.user_profile, name='user_profile'),
    path('export/xlsx/', export_user_data_xlsx, name='export_user_data_xlsx'),

    # Cloud and Budget Actions
    path('connect-cloud/', views.connect_cloud, name='connect_cloud'),
    path('set-budget/', views.set_budget, name='set_budget'),

    # Subscriptions
    path('subscriptions/', views.subscription_list, name='subscription_list'),

    # APIs
    path('api/', include('cloud_mgmt_tool.subscription_manager.api_urls')),
    path('api/cloud/<str:provider>/', list_cloud_resources, name='list_cloud'),
    path('api/subscription/<str:provider>/<str:email>/', create_subscription, name='create_subscription'),
    path('api/login/<str:provider>/', login_redirect, name='login_redirect'),

    # Misc
    path('google-popup/', TemplateView.as_view(template_name="accounts/google_popup.html"), name="google_popup"),

    # Admin
    path('admin/', admin.site.urls),
]
