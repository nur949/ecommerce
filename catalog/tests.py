from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class CatalogCartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Gadgets', slug='gadgets')
        self.product = Product.objects.create(
            category=self.category,
            name='Wireless Mouse',
            slug='wireless-mouse',
            description='Reliable wireless mouse.',
            price='1200.00',
            compare_at_price='1500.00',
            sku='WM-001',
            stock=2,
            is_active=True,
        )

    def test_ajax_add_to_cart_respects_stock_limit(self):
        url = reverse('catalog:add_to_cart', args=[self.product.slug])
        for _ in range(3):
            response = self.client.post(
                url,
                {'quantity': 1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            )
            self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['cart_count'], 2)

    def test_shop_supports_sorting(self):
        Product.objects.create(
            category=self.category,
            name='Budget Keyboard',
            slug='budget-keyboard',
            description='Entry keyboard.',
            price='500.00',
            sku='BK-001',
            stock=5,
            is_active=True,
        )
        response = self.client.get(reverse('catalog:shop'), {'sort': 'price_low'})
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0].name, 'Budget Keyboard')
