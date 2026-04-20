from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product


class HomeSectionTests(TestCase):
    def test_popular_categories_render_count_and_empty_state_hooks(self):
        category = Category.objects.create(
            name='Skincare',
            slug='skincare',
            is_featured=True,
            description='Daily skincare routines for healthy and balanced skin.',
        )
        Product.objects.create(
            category=category,
            name='Glow Cleanser',
            slug='glow-cleanser',
            description='Cleanser',
            price='450.00',
            sku='GC-001',
            stock=10,
            is_active=True,
        )

        response = self.client.get(reverse('core:home'), HTTP_HOST='testserver')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Top Categories')
        self.assertContains(response, 'Skincare')
        self.assertContains(response, 'See All')
        self.assertContains(response, 'top-category-item')
        self.assertNotContains(response, 'popular-category-card')
