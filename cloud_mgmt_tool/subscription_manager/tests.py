# subscription_manager/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloud_mgmt_tool.settings")
django.setup()

class RegistrationPageTests(TestCase):

    def test_registration_page_status_code(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_registration_form(self):
        # Post data to the registration view and verify a new user is created.
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())

class HomePageTests(TestCase):

    def test_home_page_status_code(self):
        # 'home' is the name of the URL pattern for your home view
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

# Create your tests here.
