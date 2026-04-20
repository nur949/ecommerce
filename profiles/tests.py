from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='nur@example.com', email='nur@example.com', password='StrongPass123')

    def test_profile_is_created_for_new_user(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profiles:profile'), HTTP_HOST='testserver')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response['Location'])

    def test_user_can_update_own_profile(self):
        self.client.login(username='nur@example.com', password='StrongPass123')

        response = self.client.post(
            reverse('profiles:profile_edit'),
            {
                'first_name': 'Nur',
                'last_name': 'Customer',
                'email': 'customer@example.com',
                'bio': 'Operations lead and repeat customer.',
                'phone': '+880 1711 111111',
                'address': 'Dhaka, Bangladesh',
                'website': 'https://example.com',
            },
            HTTP_HOST='testserver',
        )

        self.assertRedirects(response, reverse('profiles:profile'), fetch_redirect_response=False)
        self.user.refresh_from_db()
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(self.user.email, 'customer@example.com')
        self.assertEqual(self.user.username, 'customer@example.com')
        self.assertEqual(profile.bio, 'Operations lead and repeat customer.')
        self.assertEqual(profile.phone, '+880 1711 111111')
