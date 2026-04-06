from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from catalog.models import Category, Product, ProductVariant
from core.models import BlogCategory, BlogPost, FooterLink, HeroSlide, NavItem, PromoBanner, SiteSettings, StaticPage


class Command(BaseCommand):
    help = 'Seed demo data for Zynvo'

    def handle(self, *args, **options):
        settings = SiteSettings.load()
        settings.site_name = 'Zynvo'
        settings.save()

        nav_items = [
            ('Home', '/'),
            ('Summer Collection', '/shop/'),
            ('Best Deals', '/shop/'),
            ('Men', '/category/men/'),
            ('Women', '/category/women/'),
            ('Kids', '/category/kids/'),
            ('Electronics', '/category/electronics/'),
        ]
        for i, (title, url) in enumerate(nav_items, start=1):
            NavItem.objects.update_or_create(title=title, location='primary', defaults={'url': url, 'order': i, 'is_active': True})

        footer_groups = {
            'company': ['Blogs', 'Outlets', 'Careers', 'About Us', 'Contact Us'],
            'customer': ['Login', 'Register', 'Best Deals', 'Shop'],
            'help': ['FAQs', 'Privacy Policy', 'Terms & Conditions', 'Return Policy'],
        }
        for group, items in footer_groups.items():
            for i, title in enumerate(items, start=1):
                FooterLink.objects.update_or_create(title=title, group=group, defaults={'url': '/pages/%s/' % title.lower().replace(' ', '-'), 'order': i, 'is_active': True})

        cats = {}
        for i, name in enumerate(['Women', 'Men', 'Kids', 'Electronics', 'Accessories', 'Bags'], start=1):
            cats[name], _ = Category.objects.update_or_create(name=name, defaults={'description': f'Shop the latest {name.lower()} products.', 'is_featured': True, 'order': i})

        for i, title in enumerate(['Style Refresh', 'Gadget Picks', 'Seasonal Savings'], start=1):
            HeroSlide.objects.update_or_create(title=title, defaults={
                'subtitle': 'Curated collections designed for modern shoppers.',
                'cta_text': 'Shop Now',
                'cta_url': '/shop/',
                'accent_label': 'Up to 38% Off' if i == 1 else 'Fresh Picks',
                'bg_color': ['#eef6ff', '#f3e8ff', '#eff6ff'][i-1],
                'order': i,
                'is_active': True,
            })

        banners = [
            ('New Arrivals', 'Explore today', '/shop/', '#f8fafc', 'hero_right'),
            ('Smart Accessories', 'Premium picks', '/category/accessories/', '#dbeafe', 'hero_right'),
            ('Office Ready', 'Clean essentials', '/corporate/', '#e2e8f0', 'hero_right'),
            ('Exclusive Collection', 'Modern gadget lineup', '/shop/', '#dbeafe', 'gadget'),
            ('Travel Smart', 'Carry with confidence', '/category/bags/', '#ede9fe', 'gadget'),
            ('Top Audio', 'Crystal-clear sound', '/category/electronics/', '#ecfccb', 'gadget'),
            ('Wireless Speaker', '', '/category/electronics/', '#dbeafe', 'unlimited'),
            ('Shoulder Backpack', '', '/category/bags/', '#fef3c7', 'unlimited'),
            ('Exclusive Earbuds', '', '/category/electronics/', '#e0f2fe', 'unlimited'),
            ('Headphones', '', '/category/electronics/', '#f3e8ff', 'unlimited'),
            ('Trimmer', '', '/category/electronics/', '#ecfccb', 'unlimited'),
            ('Smart Watch', '', '/category/electronics/', '#fee2e2', 'unlimited'),
        ]
        for i, (title, subtitle, url, color, group) in enumerate(banners, start=1):
            PromoBanner.objects.update_or_create(title=title, group=group, defaults={'subtitle': subtitle, 'url': url, 'color': color, 'order': i, 'is_active': True})

        products = [
            ('Zynvo Glow Smart Watch', cats['Electronics'], 2180, 2400, 'ZY-SW-001', True, True, True, 'Watch'),
            ('Urban Flex Backpack', cats['Bags'], 1850, 2200, 'ZY-BG-002', True, True, False, 'Bags & Luggage'),
            ('Velvet Everyday Tote', cats['Women'], 1490, 1890, 'ZY-WM-003', False, True, True, 'Bags & Luggage'),
            ('Pulse Wireless Earbuds', cats['Electronics'], 2490, 2990, 'ZY-EL-004', True, True, True, 'Headphones'),
            ('Minimal Office Shirt', cats['Men'], 1290, 1590, 'ZY-MN-005', False, True, False, 'General'),
            ('Bright Kids Set', cats['Kids'], 990, 1290, 'ZY-KD-006', False, True, False, 'General'),
            ('Signature Crossbody', cats['Women'], 1690, 1990, 'ZY-WM-007', True, True, False, 'Bags & Luggage'),
            ('Travel Lite Duffle', cats['Bags'], 2100, 2500, 'ZY-BG-008', True, False, True, 'Bags & Luggage'),
            ('Noise-Free Headset', cats['Electronics'], 3250, 3750, 'ZY-EL-009', True, False, True, 'Headphones'),
            ('Trim Pro Groomer', cats['Electronics'], 1450, 1750, 'ZY-EL-010', True, False, True, 'Shaving & Trimming'),
            ('Aura Satin Dress', cats['Women'], 2890, 3490, 'ZY-WM-011', False, True, False, 'General'),
            ('Core Casual Tee', cats['Men'], 850, 990, 'ZY-MN-012', False, True, False, 'General'),
        ]
        for idx, (name, category, price, compare_at, sku, deal, is_new, trending, group) in enumerate(products, start=1):
            product, _ = Product.objects.update_or_create(sku=sku, defaults={
                'name': name,
                'category': category,
                'short_description': 'A polished pick from Zynvo.',
                'description': f'{name} is crafted for daily comfort and style. Perfect for shoppers who want premium value with practical performance.',
                'specifications': 'Material: Premium blend\nCare: Easy clean\nOrigin: Bangladesh',
                'price': price,
                'compare_at_price': compare_at,
                'stock': 10 + idx,
                'is_active': True,
                'is_featured': idx % 2 == 0,
                'is_new': is_new,
                'is_daily_deal': deal,
                'is_trending': trending,
                'collection_label': 'Signature' if idx <= 4 else '',
                'trending_group': group,
                'deal_ends_at': timezone.now() + timedelta(days=2),
                'meta_title': name,
                'meta_description': f'Buy {name} online at Zynvo with fast delivery in Bangladesh.',
            })
            if idx <= 4:
                ProductVariant.objects.update_or_create(product=product, value='Black', defaults={'attribute_name': 'Color', 'color_hex': '#111827', 'sku': f'{sku}-BLK', 'stock': product.stock, 'is_default': True})
                ProductVariant.objects.update_or_create(product=product, value='Gold', defaults={'attribute_name': 'Color', 'color_hex': '#d4a017', 'sku': f'{sku}-GLD', 'stock': product.stock - 2})

        page_titles = ['about-us', 'contact-us', 'privacy-policy', 'terms-&-conditions', 'return-policy', 'faqs', 'blogs', 'careers']
        for slug in page_titles:
            StaticPage.objects.update_or_create(slug=slug, defaults={'title': slug.replace('-', ' ').title(), 'body': 'This is a demo content page for Zynvo.', 'is_published': True})

        blog_cat, _ = BlogCategory.objects.get_or_create(name='Guides', slug='guides')
        BlogPost.objects.update_or_create(slug='best-everyday-essentials', defaults={'category': blog_cat, 'title': 'Best Everyday Essentials for 2026', 'excerpt': 'Explore practical picks for home, work, and travel.', 'content': 'Zynvo curates products that blend function and style. This guide highlights simple ways to build a stronger everyday collection.', 'is_published': True})

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@zynvo.com', 'admin12345')
            self.stdout.write(self.style.WARNING('Created admin user: admin / admin12345'))

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
