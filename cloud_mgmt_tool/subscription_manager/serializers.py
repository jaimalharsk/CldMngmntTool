from rest_framework import serializers
from .models import CloudServiceSubscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudServiceSubscription
        fields = '__all__'

