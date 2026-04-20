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
            data='{"username": "apiuser", "password": "StrongPass123"}',
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
