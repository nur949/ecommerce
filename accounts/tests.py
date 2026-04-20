from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from .models import UserProfile, WishlistItem


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


class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='nur', email='nur@example.com', password='StrongPass123')

    def test_user_can_login_with_email_address(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'nur@example.com', 'password': 'StrongPass123'},
            HTTP_HOST='testserver',
        )

        self.assertRedirects(response, reverse('accounts:dashboard'), fetch_redirect_response=False)


class DashboardProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='nur', email='nur@example.com', password='StrongPass123')

    def test_user_can_update_full_profile_from_dashboard(self):
        self.client.login(username='nur', password='StrongPass123')

        response = self.client.post(
            reverse('accounts:dashboard'),
            {
                'action': 'profile',
                'name': 'Nur Customer',
                'email': 'customer@example.com',
                'phone': '+880 1711 111111',
                'birthday': '1995-04-21',
                'preferred_brands': 'COSRX, Fenty Beauty',
                'beauty_preferences': 'Sensitive skin and fragrance free products.',
            },
            HTTP_HOST='testserver',
        )

        self.assertRedirects(response, reverse('accounts:dashboard'), fetch_redirect_response=False)
        self.user.refresh_from_db()
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(self.user.first_name, 'Nur Customer')
        self.assertEqual(self.user.email, 'customer@example.com')
        self.assertEqual(profile.phone, '+880 1711 111111')
        self.assertEqual(profile.birthday.isoformat(), '1995-04-21')
        self.assertEqual(profile.preferred_brands, 'COSRX, Fenty Beauty')
        self.assertEqual(profile.beauty_preferences, 'Sensitive skin and fragrance free products.')
        self.assertFalse(profile.marketing_opt_in)

    def test_password_errors_are_rendered_on_dashboard(self):
        self.client.login(username='nur', password='StrongPass123')

        response = self.client.post(
            reverse('accounts:dashboard'),
            {
                'action': 'password',
                'old_password': 'wrong-password',
                'new_password1': 'NewStrongPass123',
                'new_password2': 'NewStrongPass123',
            },
            HTTP_HOST='testserver',
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your old password was entered incorrectly.')


class WishlistTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='nur', email='nur@example.com', password='StrongPass123')
        category = Category.objects.create(name='Beauty', slug='beauty')
        self.product = Product.objects.create(
            category=category,
            name='Glow Serum',
            slug='glow-serum',
            description='Brightening serum.',
            price='999.00',
            sku='GS-001',
            stock=5,
            is_active=True,
        )

    def test_authenticated_user_can_add_product_to_wishlist(self):
        self.client.login(username='nur', password='StrongPass123')
        response = self.client.post(reverse('accounts:add_to_wishlist', args=[self.product.slug]), {'next': reverse('catalog:shop')}, HTTP_HOST='testserver')
        self.assertRedirects(response, reverse('catalog:shop'), fetch_redirect_response=False)
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

    def test_ajax_wishlist_add_returns_updated_state(self):
        self.client.login(username='nur', password='StrongPass123')
        response = self.client.post(
            reverse('accounts:add_to_wishlist', args=[self.product.slug]),
            {'next': reverse('catalog:shop')},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='testserver',
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['ok'])
        self.assertTrue(data['is_wishlisted'])
        self.assertEqual(data['wishlist_count'], 1)
        self.assertEqual(data['product_id'], self.product.id)

    def test_authenticated_user_can_remove_product_from_wishlist(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        self.client.login(username='nur', password='StrongPass123')
        response = self.client.post(reverse('accounts:remove_from_wishlist', args=[self.product.slug]), {'next': reverse('accounts:wishlist')}, HTTP_HOST='testserver')
        self.assertRedirects(response, reverse('accounts:wishlist'), fetch_redirect_response=False)
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

    def test_ajax_wishlist_remove_returns_updated_state(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        self.client.login(username='nur', password='StrongPass123')
        response = self.client.post(
            reverse('accounts:remove_from_wishlist', args=[self.product.slug]),
            {'next': reverse('accounts:wishlist')},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='testserver',
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['ok'])
        self.assertFalse(data['is_wishlisted'])
        self.assertEqual(data['wishlist_count'], 0)
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

    def test_wishlist_page_requires_login(self):
        response = self.client.get(reverse('accounts:wishlist'), HTTP_HOST='testserver')
        self.assertEqual(response.status_code, 302)


class AccountApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', email='api@example.com', password='StrongPass123')

    def test_profile_api_rejects_invalid_birthday(self):
        login_response = self.client.post(
            reverse('accounts:api_login'),
            data='{"email": "api@example.com", "password": "StrongPass123"}',
            content_type='application/json',
            HTTP_HOST='testserver',
        )
        token = login_response.json()['token']

        response = self.client.patch(
            reverse('accounts:api_profile'),
            data='{"birthday": "20-04-2026"}',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
            HTTP_HOST='testserver',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['ok'])
        self.assertFalse(UserProfile.objects.filter(user=self.user, birthday__isnull=False).exists())
