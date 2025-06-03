# yourapp/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.account.utils import user_email, user_field

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If user already logged in, do nothing
        if request.user.is_authenticated:
            return

        email = user_email(sociallogin.user)

        if email:
            User = get_user_model()
            try:
                existing_user = User.objects.get(email=email)
                # Connect this social account to the existing user
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass  # No user with this email exists, proceed as normal
