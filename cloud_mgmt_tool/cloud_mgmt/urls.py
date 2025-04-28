from django.contrib import admin
from django.urls import path, include
from subscription_manager.views import AdminStyleLoginView  # ✅ Correct import
from subscription_manager.auth_views import register  # ✅ Custom registration view

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('accounts/', include('django.contrib.auth.urls')),  # Django built-in auth views (login, logout, etc.)
    path('accounts/register/', register, name='register'),  # Custom user registration
    path('accounts/login/', AdminStyleLoginView.as_view(), name='login'),  # Login page
    path('', include('subscription_manager.urls')),  # Include app-specific URLs
]


