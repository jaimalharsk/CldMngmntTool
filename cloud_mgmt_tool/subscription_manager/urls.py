from . import views
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import list_cloud_resources, create_subscription, login_redirect
from django.views.generic import TemplateView


urlpatterns = [
    # Include allauth.urls for Google OAuth
    path('accounts/', include('allauth.urls')),
    path('profile/', views.user_profile, name='user_profile'),
    path('export/', views.export_user_data, name='export_user_data'),
    # Use LoginView for the login page
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('registration/', views.register, name='register'),
    path('api/', include('subscription_manager.api_urls')),
    path('api/cloud/<str:provider>/', list_cloud_resources, name='list_cloud'),
    path('api/subscription/<str:provider>/<str:email>/', create_subscription, name='create_subscription'),
    path('api/login/<str:provider>/', login_redirect, name='login_redirect'),
    path('dashboard/', views.dashboard, name='dashboard'),  # ✅ Correct dashboard route
    path('google-popup/', TemplateView.as_view(template_name="accounts/google_popup.html"), name="google_popup"),
]
