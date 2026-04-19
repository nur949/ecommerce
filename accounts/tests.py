from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class PasswordResetTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='nur', email='nur@example.com', password='StrongPass123')

    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse('accounts:password_reset'), HTTP_HOST='testserver')
        self.assertEqual(response.status_code, 200)

    def test_password_reset_submission_redirects_to_done(self):
        response = self.client.post(
            reverse('accounts:password_reset'),
            {'email': 'nur@example.com'},
            HTTP_HOST='testserver',
        )
        self.assertRedirects(response, reverse('accounts:password_reset_done'), fetch_redirect_response=False)
