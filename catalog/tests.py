from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, ProductVariant


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
        self.assertIn('cart_totals', response.json())

    def test_ajax_cart_update_returns_summary_totals(self):
        self.client.post(reverse('catalog:add_to_cart', args=[self.product.slug]), {'quantity': 1})
        response = self.client.post(
            reverse('catalog:update_cart'),
            {'item_key': f'{self.product.id}:0', 'quantity': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='testserver',
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['ok'])
        self.assertEqual(data['item_quantity'], 2)
        self.assertEqual(data['cart_totals']['subtotal'], '2400.00')

    def test_ajax_cart_remove_returns_summary_totals(self):
        self.client.post(reverse('catalog:add_to_cart', args=[self.product.slug]), {'quantity': 1})
        response = self.client.post(
            reverse('catalog:remove_cart_item', args=[f'{self.product.id}:0']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='testserver',
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['ok'])
        self.assertEqual(data['cart_count'], 0)
        self.assertEqual(data['cart_totals']['total'], '0.00')

    def test_cart_remove_requires_post_and_csrf_protected_form(self):
        self.client.post(reverse('catalog:add_to_cart', args=[self.product.slug]), {'quantity': 1})
        item_key = f'{self.product.id}:0'

        get_response = self.client.get(reverse('catalog:remove_cart_item', args=[item_key]), HTTP_HOST='testserver')
        self.assertEqual(get_response.status_code, 405)

        cart_response = self.client.get(reverse('orders:cart'), HTTP_HOST='testserver')
        self.assertContains(cart_response, 'js-cart-remove-form')

        post_response = self.client.post(reverse('catalog:remove_cart_item', args=[item_key]), HTTP_HOST='testserver')
        self.assertRedirects(post_response, reverse('orders:cart'), fetch_redirect_response=False)
        self.assertEqual(self.client.session.get('cart'), {})

    def test_cart_items_clamp_stale_session_quantity_to_current_stock(self):
        self.client.post(reverse('catalog:add_to_cart', args=[self.product.slug]), {'quantity': 2})
        self.product.stock = 1
        self.product.save(update_fields=['stock'])

        response = self.client.get(reverse('orders:cart'), HTTP_HOST='testserver')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="1"')
        self.assertNotContains(response, 'value="2"')

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

    def test_sale_query_redirects_to_normal_shop(self):
        response = self.client.get(reverse('catalog:shop'), {'sale': '1'}, HTTP_HOST='testserver')

        self.assertRedirects(response, reverse('catalog:shop'), fetch_redirect_response=False)

    def test_sale_query_redirect_preserves_other_filters(self):
        response = self.client.get(
            reverse('catalog:shop'),
            {'sale': '1', 'q': 'mouse', 'sort': 'name'},
            HTTP_HOST='testserver',
        )

        self.assertRedirects(response, f'{reverse("catalog:shop")}?q=mouse&sort=name', fetch_redirect_response=False)

    def test_shop_ajax_returns_grouped_sections_and_category_nav(self):
        response = self.client.get(
            reverse('catalog:shop'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='testserver',
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['ok'])
        self.assertIn('shop-category-section', data['html'])
        self.assertIn('data-category="gadgets"', data['nav_html'])
        self.assertIn('col-xl-3', data['html'])
        self.assertNotIn('col-xxl-2', data['html'])

    def test_parent_category_pages_include_child_products(self):
        parent = Category.objects.create(name='Beauty', slug='beauty')
        child = Category.objects.create(name='Serums', slug='serums', parent=parent)
        product = Product.objects.create(
            category=child,
            name='Glow Serum',
            slug='glow-serum',
            description='Brightening serum.',
            price='999.00',
            sku='GS-001',
            stock=4,
            is_active=True,
        )

        category_response = self.client.get(reverse('catalog:category_detail', args=[parent.slug]), HTTP_HOST='testserver')
        shop_response = self.client.get(reverse('catalog:shop'), {'category': parent.slug}, HTTP_HOST='testserver')

        self.assertContains(category_response, product.name)
        self.assertContains(shop_response, product.name)

    def test_product_detail_renders_purchase_summary_hooks(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            attribute_name='Size',
            value='Mini',
            sku='WM-001-MINI',
            price_override='900.00',
            stock=2,
            is_default=True,
        )

        response = self.client.get(reverse('catalog:product_detail', args=[self.product.slug]), HTTP_HOST='testserver')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'detailTotalPrice')
        self.assertContains(response, 'detailSku')
        self.assertContains(response, 'product-qty-controls')
        self.assertContains(response, variant.sku)

    def test_product_detail_disables_initial_out_of_stock_variant(self):
        ProductVariant.objects.create(
            product=self.product,
            attribute_name='Size',
            value='Sold out',
            sku='WM-001-SOLD',
            price_override='900.00',
            stock=0,
            is_default=True,
        )

        response = self.client.get(reverse('catalog:product_detail', args=[self.product.slug]), HTTP_HOST='testserver')

        self.assertContains(response, 'id="addToCartButton" disabled')
        self.assertContains(response, 'Out of Stock')

    def test_product_card_sends_variant_products_to_detail_page(self):
        ProductVariant.objects.create(
            product=self.product,
            attribute_name='Size',
            value='Mini',
            sku='WM-001-MINI',
            price_override='900.00',
            stock=2,
            is_default=True,
        )

        response = self.client.get(reverse('catalog:shop'), HTTP_HOST='testserver')

        self.assertContains(response, 'Choose Options')
        self.assertNotContains(response, f'action="{reverse("catalog:add_to_cart", args=[self.product.slug])}"')

    def test_products_api_handles_invalid_page_size(self):
        response = self.client.get(reverse('catalog:api_products'), {'page_size': 'bad'}, HTTP_HOST='testserver')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])

    def test_review_api_rejects_invalid_json(self):
        response = self.client.post(
            reverse('catalog:api_submit_review', args=[self.product.slug]),
            data='not-json',
            content_type='application/json',
            HTTP_HOST='testserver',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['ok'])
