from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from .models import Order


class CheckoutFlowTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Beauty', slug='beauty')
        self.product = Product.objects.create(
            category=category,
            name='Daily Serum',
            slug='daily-serum',
            description='Hydrating serum.',
            price='900.00',
            sku='DS-001',
            stock=3,
            is_active=True,
        )

    def test_checkout_creates_order_and_reduces_stock(self):
        self.client.post(reverse('catalog:add_to_cart', args=[self.product.slug]), {'quantity': 2})
        response = self.client.post(reverse('orders:checkout'), {
            'full_name': 'Test Customer',
            'phone': '+880 1700 000000',
            'country': 'Bangladesh',
            'city': 'Dhaka',
            'area': 'Dhanmondi',
            'postcode': '1209',
            'address_line': 'House 1, Road 2, Dhanmondi',
            'delivery_type': 'home',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

    def test_guest_cannot_open_other_order_detail_by_guessing_number(self):
        order = Order.objects.create(
            order_number='ZYSECURE1',
            subtotal='10.00',
            total='10.00',
        )
        response = self.client.get(reverse('orders:detail', args=[order.order_number]), HTTP_HOST='testserver')
        self.assertEqual(response.status_code, 404)

    def test_checkout_grants_session_access_to_created_order(self):
        self.client.post(reverse('catalog:add_to_cart', args=[self.product.slug]), {'quantity': 1}, HTTP_HOST='testserver')
        checkout_response = self.client.post(reverse('orders:checkout'), {
            'full_name': 'Test Customer',
            'phone': '+880 1700 000000',
            'country': 'Bangladesh',
            'city': 'Dhaka',
            'area': 'Dhanmondi',
            'postcode': '1209',
            'address_line': 'House 1, Road 2, Dhanmondi',
            'delivery_type': 'home',
        }, HTTP_HOST='testserver')
        order = Order.objects.get()

        detail_response = self.client.get(reverse('orders:detail', args=[order.order_number]), HTTP_HOST='testserver')

        self.assertEqual(checkout_response.status_code, 302)
        self.assertEqual(detail_response.status_code, 200)
