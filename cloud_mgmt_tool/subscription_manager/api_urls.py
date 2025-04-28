from django.urls import path
from .views import subscription_list_api

urlpatterns = [
    path('subscriptions/', subscription_list_api, name='subscription_list_api'),
]
