from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Category, Product, ProductVariant
from core.models import (
    BlogCategory,
    BlogPost,
    FooterLink,
    HeroSlide,
    NavItem,
    PromoBanner,
    SiteSettings,
    StaticPage,
)


class Command(BaseCommand):
    help = 'Seed demo data for Zynvo'

    def handle(self, *args, **options):
        settings = SiteSettings.load()
        settings.site_name = 'Zynvo'
        settings.tagline = 'Beauty, fashion, and smart essentials in one place.'
        settings.hero_title = 'Glow Every Day With Curated Beauty Picks'
        settings.hero_subtitle = 'Shop trending cosmetics, skincare, haircare, fragrance, and daily essentials with fast delivery.'
        settings.announcement_text = 'Free delivery on beauty orders over 3000 BDT'
        settings.save()

        nav_items = [
            ('Home', '/'),
            ('Cosmetics', '/category/cosmetics/'),
            ('Skincare', '/category/skincare/'),
            ('Haircare', '/category/haircare/'),
            ('Fragrance', '/category/fragrance/'),
            ('Women', '/category/women/'),
            ('Men', '/category/men/'),
            ('Kids', '/category/kids/'),
            ('Electronics', '/category/electronics/'),
            ('Shop', '/shop/'),
        ]
        for i, (title, url) in enumerate(nav_items, start=1):
            NavItem.objects.update_or_create(
                title=title,
                location='primary',
                defaults={'url': url, 'order': i, 'is_active': True},
            )

        footer_groups = {
            'company': ['Blogs', 'Outlets', 'Careers', 'About Us', 'Contact Us'],
            'customer': ['Login', 'Register', 'Best Deals', 'Shop'],
            'help': ['FAQs', 'Privacy Policy', 'Terms & Conditions', 'Return Policy'],
        }
        for group, items in footer_groups.items():
            for i, title in enumerate(items, start=1):
                FooterLink.objects.update_or_create(
                    title=title,
                    group=group,
                    defaults={'url': '/pages/%s/' % title.lower().replace(' ', '-'), 'order': i, 'is_active': True},
                )

        category_specs = [
            ('cosmetics', 'Cosmetics', None, 1, 'Complete makeup essentials for daily and glam looks.'),
            ('skincare', 'Skincare', None, 2, 'Daily skincare routines for healthy and balanced skin.'),
            ('haircare', 'Haircare', None, 3, 'Shampoo, treatments, and styling essentials.'),
            ('fragrance', 'Fragrance', None, 4, 'Long-lasting perfume and body mist collections.'),
            ('women', 'Women', None, 5, 'Women fashion and lifestyle picks.'),
            ('men', 'Men', None, 6, 'Men fashion and daily essentials.'),
            ('kids', 'Kids', None, 7, 'Kids clothing, care, and accessories.'),
            ('electronics', 'Electronics', None, 8, 'Smart gadgets and personal devices.'),
            ('cos_lips', 'Lips', 'cosmetics', 1, 'Lipstick, gloss, tint, and liner picks.'),
            ('cos_face', 'Face Base', 'cosmetics', 2, 'Foundation, powder, and concealer products.'),
            ('cos_eyes', 'Eye Makeup', 'cosmetics', 3, 'Mascara, eyeliner, brows, and palettes.'),
            ('cos_nails', 'Nails', 'cosmetics', 4, 'Nail polish and manicure essentials.'),
            ('cos_tools', 'Beauty Tools', 'cosmetics', 5, 'Brushes, blenders, and makeup tools.'),
            ('skin_cleanser', 'Cleansers', 'skincare', 1, 'Face wash and cleansing care products.'),
            ('skin_serum', 'Serums', 'skincare', 2, 'Targeted serum formulas for daily glow.'),
            ('skin_moisturizer', 'Moisturizers', 'skincare', 3, 'Hydration creams and gels.'),
            ('skin_suncare', 'Sun Care', 'skincare', 4, 'Sunscreen and UV protection products.'),
            ('hair_wash', 'Hair Wash', 'haircare', 1, 'Shampoo and conditioner essentials.'),
            ('hair_treatment', 'Hair Treatments', 'haircare', 2, 'Hair mask, oil, and serum care.'),
            ('hair_style', 'Hair Styling', 'haircare', 3, 'Styling creams and finishing products.'),
            ('frag_women', 'Women Perfume', 'fragrance', 1, 'Women fragrances and signature scents.'),
            ('frag_men', 'Men Perfume', 'fragrance', 2, 'Men fragrances for daily and evening wear.'),
            ('frag_mist', 'Body Mist', 'fragrance', 3, 'Fresh body mists and spray collections.'),
            ('men_groom', 'Men Grooming', 'men', 1, 'Shaving and grooming tools for men.'),
            ('elec_audio', 'Audio', 'electronics', 1, 'Headphones, earbuds, and speakers.'),
            ('elec_wearable', 'Wearables', 'electronics', 2, 'Smartwatch and wearable gadgets.'),
        ]

        cats = {}
        for key, name, parent_key, order, description in category_specs:
            parent = cats.get(parent_key)
            cat, _ = Category.objects.update_or_create(
                name=name,
                defaults={
                    'parent': parent,
                    'description': description,
                    'is_featured': parent is None,
                    'order': order,
                    'meta_title': f'{name} | Zynvo',
                    'meta_description': description,
                },
            )
            if cat.parent_id != (parent.id if parent else None):
                cat.parent = parent
                cat.save(update_fields=['parent'])
            cats[key] = cat

        hero_slides = [
            ('Glow & Go Makeup', 'Discover trending lipstick, base, and eye looks for every day.', '/category/cosmetics/', 'Top Beauty Picks', '#fde7ef'),
            ('Skincare Routine Builder', 'Layer cleanser, serum, moisturizer, and SPF the right way.', '/category/skincare/', 'Daily Care', '#e7f7f4'),
            ('Fragrance Wardrobe', 'Choose signature perfume and mist for work, date, and travel.', '/category/fragrance/', 'Long Lasting', '#efe8ff'),
        ]
        for i, (title, subtitle, url, accent, color) in enumerate(hero_slides, start=1):
            HeroSlide.objects.update_or_create(
                title=title,
                defaults={
                    'subtitle': subtitle,
                    'cta_text': 'Shop Now',
                    'cta_url': url,
                    'accent_label': accent,
                    'bg_color': color,
                    'order': i,
                    'is_active': True,
                },
            )

        banners = [
            ('Lip & Cheek Edit', 'New shades this week', '/category/cosmetics/', '#ffe4ef', 'hero_right'),
            ('Serum Spotlight', 'Hydrate and brighten', '/category/skincare/', '#dff7f2', 'hero_right'),
            ('Perfume Bestsellers', 'Fresh and floral tones', '/category/fragrance/', '#efe7ff', 'hero_right'),
            ('Beauty Blender Set', 'Soft finish tools', '/category/cosmetics/', '#fce7f3', 'gadget'),
            ('Vitamin C Serum', 'Daily glow formula', '/category/skincare/', '#ecfeff', 'gadget'),
            ('Hair Oil Treatment', 'Smooth and repair', '/category/haircare/', '#fef9c3', 'gadget'),
            ('Matte Lipstick Kit', '', '/category/cosmetics/', '#fbcfe8', 'unlimited'),
            ('SPF50 Sunscreen', '', '/category/skincare/', '#d9f99d', 'unlimited'),
            ('Night Repair Serum', '', '/category/skincare/', '#bae6fd', 'unlimited'),
            ('Woody Men Perfume', '', '/category/fragrance/', '#e9d5ff', 'unlimited'),
            ('Keratin Hair Mask', '', '/category/haircare/', '#fef3c7', 'unlimited'),
            ('Wireless Earbuds', '', '/category/electronics/', '#dbeafe', 'unlimited'),
        ]
        for i, (title, subtitle, url, color, group) in enumerate(banners, start=1):
            PromoBanner.objects.update_or_create(
                title=title,
                group=group,
                defaults={'subtitle': subtitle, 'url': url, 'color': color, 'order': i, 'is_active': True},
            )

        products = [
            ('Velvet Matte Lipstick Ruby Red', 'cos_lips', 790, 990, 'ZY-COS-LIP-001', 'Zynvo Beauty', 'Makeup', True, True, True, 'Best Seller'),
            ('Hydra Shine Lip Gloss Crystal', 'cos_lips', 650, 850, 'ZY-COS-LIP-002', 'Zynvo Beauty', 'Makeup', False, True, True, ''),
            ('Soft Nude Lip Liner Precision', 'cos_lips', 390, 490, 'ZY-COS-LIP-003', 'Zynvo Beauty', 'Makeup', False, False, False, ''),
            ('Tinted Lip Balm Rose Dew', 'cos_lips', 450, 590, 'ZY-COS-LIP-004', 'Zynvo Beauty', 'Makeup', True, False, True, ''),
            ('Longwear Liquid Lipstick Mocha', 'cos_lips', 840, 1040, 'ZY-COS-LIP-005', 'Zynvo Beauty', 'Makeup', False, True, False, ''),
            ('24H Transferproof Lip Tint Berry', 'cos_lips', 720, 920, 'ZY-COS-LIP-006', 'Zynvo Beauty', 'Makeup', True, True, True, ''),
            ('Silk Finish Foundation Warm Beige', 'cos_face', 1190, 1490, 'ZY-COS-FACE-001', 'Zynvo Beauty', 'Makeup', True, True, True, 'Hot'),
            ('Air Blur Compact Powder Natural', 'cos_face', 880, 1080, 'ZY-COS-FACE-002', 'Zynvo Beauty', 'Makeup', False, False, True, ''),
            ('Hydra Grip Face Primer Clear', 'cos_face', 980, 1180, 'ZY-COS-FACE-003', 'Zynvo Beauty', 'Makeup', False, True, False, ''),
            ('Full Cover Concealer Sand', 'cos_face', 760, 920, 'ZY-COS-FACE-004', 'Zynvo Beauty', 'Makeup', False, True, True, ''),
            ('Velvet Cream Blush Coral', 'cos_face', 690, 890, 'ZY-COS-FACE-005', 'Zynvo Beauty', 'Makeup', True, False, True, ''),
            ('Glow Beam Liquid Highlighter Gold', 'cos_face', 820, 990, 'ZY-COS-FACE-006', 'Zynvo Beauty', 'Makeup', False, True, True, ''),
            ('Ultra Length Mascara Black', 'cos_eyes', 710, 890, 'ZY-COS-EYE-001', 'Zynvo Beauty', 'Makeup', True, True, True, ''),
            ('Precision Liquid Eyeliner Jet', 'cos_eyes', 620, 790, 'ZY-COS-EYE-002', 'Zynvo Beauty', 'Makeup', False, False, True, ''),
            ('Brow Definer Pencil Dark Brown', 'cos_eyes', 480, 620, 'ZY-COS-EYE-003', 'Zynvo Beauty', 'Makeup', False, True, False, ''),
            ('Nude Eye Shadow Palette 12 Color', 'cos_eyes', 1290, 1590, 'ZY-COS-EYE-004', 'Zynvo Beauty', 'Makeup', True, True, True, 'Trending'),
            ('Volume Lash Mascara Waterproof', 'cos_eyes', 760, 940, 'ZY-COS-EYE-005', 'Zynvo Beauty', 'Makeup', False, False, True, ''),
            ('Glitter Eye Shadow Quad Rose', 'cos_eyes', 840, 1020, 'ZY-COS-EYE-006', 'Zynvo Beauty', 'Makeup', True, True, False, ''),
            ('Quick Dry Nail Polish Cherry', 'cos_nails', 330, 450, 'ZY-COS-NAIL-001', 'Zynvo Beauty', 'Makeup', False, True, False, ''),
            ('Gel Finish Nail Polish Nude', 'cos_nails', 360, 480, 'ZY-COS-NAIL-002', 'Zynvo Beauty', 'Makeup', False, False, True, ''),
            ('French Manicure Nail Kit', 'cos_nails', 940, 1220, 'ZY-COS-NAIL-003', 'Zynvo Beauty', 'Makeup', True, True, True, ''),
            ('Nail Strengthener Treatment', 'cos_nails', 420, 560, 'ZY-COS-NAIL-004', 'Zynvo Beauty', 'Makeup', False, False, False, ''),
            ('Professional Makeup Brush Set 12', 'cos_tools', 1350, 1690, 'ZY-COS-TOOL-001', 'Zynvo Beauty', 'Makeup', True, True, True, ''),
            ('Beauty Blender Sponge Duo', 'cos_tools', 520, 680, 'ZY-COS-TOOL-002', 'Zynvo Beauty', 'Makeup', False, True, True, ''),
            ('Precision Concealer Brush Pro', 'cos_tools', 420, 560, 'ZY-COS-TOOL-003', 'Zynvo Beauty', 'Makeup', False, False, False, ''),
            ('Travel Makeup Brush Pouch', 'cos_tools', 690, 860, 'ZY-COS-TOOL-004', 'Zynvo Beauty', 'Makeup', False, True, False, ''),
            ('Gentle Foaming Cleanser 150ml', 'skin_cleanser', 780, 980, 'ZY-SKIN-CLN-001', 'Zynvo Derma', 'Skincare', True, True, True, ''),
            ('Hydrating Gel Cleanser 120ml', 'skin_cleanser', 720, 910, 'ZY-SKIN-CLN-002', 'Zynvo Derma', 'Skincare', False, False, True, ''),
            ('Vitamin C Brightening Serum', 'skin_serum', 1290, 1590, 'ZY-SKIN-SER-001', 'Zynvo Derma', 'Skincare', True, True, True, 'Top Rated'),
            ('Niacinamide Repair Serum', 'skin_serum', 1190, 1490, 'ZY-SKIN-SER-002', 'Zynvo Derma', 'Skincare', True, True, True, ''),
            ('Hyaluronic Acid Serum Booster', 'skin_serum', 1090, 1390, 'ZY-SKIN-SER-003', 'Zynvo Derma', 'Skincare', False, False, True, ''),
            ('Ceramide Moisturizer Cream', 'skin_moisturizer', 980, 1240, 'ZY-SKIN-MOI-001', 'Zynvo Derma', 'Skincare', False, True, False, ''),
            ('Oil Free Moisturizer Gel', 'skin_moisturizer', 950, 1190, 'ZY-SKIN-MOI-002', 'Zynvo Derma', 'Skincare', False, False, True, ''),
            ('SPF50 Sunscreen Aqua Shield', 'skin_suncare', 890, 1090, 'ZY-SKIN-SUN-001', 'Zynvo Derma', 'Skincare', True, True, True, 'Bestseller'),
            ('Matte Sunscreen SPF50 PA++++', 'skin_suncare', 920, 1150, 'ZY-SKIN-SUN-002', 'Zynvo Derma', 'Skincare', True, False, True, ''),
            ('Keratin Repair Shampoo', 'hair_wash', 760, 960, 'ZY-HAIR-WSH-001', 'Zynvo Hair', 'Haircare', False, True, True, ''),
            ('Argan Smooth Conditioner', 'hair_wash', 760, 960, 'ZY-HAIR-WSH-002', 'Zynvo Hair', 'Haircare', False, False, True, ''),
            ('Deep Restore Hair Mask', 'hair_treatment', 990, 1240, 'ZY-HAIR-TRT-001', 'Zynvo Hair', 'Haircare', True, True, True, ''),
            ('Anti Frizz Hair Serum', 'hair_treatment', 820, 1020, 'ZY-HAIR-TRT-002', 'Zynvo Hair', 'Haircare', False, True, True, ''),
            ('Nourishing Hair Oil 100ml', 'hair_treatment', 680, 860, 'ZY-HAIR-TRT-003', 'Zynvo Hair', 'Haircare', False, False, True, ''),
            ('Flexible Hold Styling Cream', 'hair_style', 620, 790, 'ZY-HAIR-STL-001', 'Zynvo Hair', 'Haircare', False, False, False, ''),
            ('Heat Protect Hair Spray', 'hair_style', 710, 890, 'ZY-HAIR-STL-002', 'Zynvo Hair', 'Haircare', False, True, True, ''),
            ('Floral Day Perfume Women', 'frag_women', 1890, 2290, 'ZY-FRG-WMN-001', 'Zynvo Scents', 'Fragrance', True, True, True, ''),
            ('Vanilla Musk Perfume Women', 'frag_women', 1990, 2390, 'ZY-FRG-WMN-002', 'Zynvo Scents', 'Fragrance', True, False, True, ''),
            ('Woody Spice Perfume Men', 'frag_men', 1950, 2350, 'ZY-FRG-MEN-001', 'Zynvo Scents', 'Fragrance', False, True, True, ''),
            ('Aqua Fresh Cologne Men', 'frag_men', 1790, 2190, 'ZY-FRG-MEN-002', 'Zynvo Scents', 'Fragrance', False, False, True, ''),
            ('Rose Bloom Body Mist', 'frag_mist', 690, 890, 'ZY-FRG-MST-001', 'Zynvo Scents', 'Fragrance', True, True, True, ''),
            ('Ocean Breeze Body Mist', 'frag_mist', 690, 890, 'ZY-FRG-MST-002', 'Zynvo Scents', 'Fragrance', True, False, True, ''),
            ('Beard Grooming Kit Pro', 'men_groom', 1450, 1790, 'ZY-MEN-GRM-001', 'Zynvo Men', 'Men Grooming', True, True, True, ''),
            ('Precision Beard Trimmer', 'men_groom', 1650, 1990, 'ZY-MEN-GRM-002', 'Zynvo Men', 'Men Grooming', True, False, True, ''),
            ('Shaving Foam Sensitive Skin', 'men_groom', 420, 540, 'ZY-MEN-GRM-003', 'Zynvo Men', 'Men Grooming', False, False, False, ''),
            ('Pulse Wireless Earbuds', 'elec_audio', 2490, 2990, 'ZY-EL-AUD-001', 'Zynvo Tech', 'Audio', True, True, True, ''),
            ('Noise Free Headphone Pro', 'elec_audio', 3290, 3890, 'ZY-EL-AUD-002', 'Zynvo Tech', 'Audio', False, True, True, ''),
            ('Glow Smart Watch Lite', 'elec_wearable', 2190, 2590, 'ZY-EL-WEA-001', 'Zynvo Tech', 'Wearables', True, True, True, ''),
            ('Urban Flex Backpack', 'women', 1850, 2200, 'ZY-WMN-ACC-001', 'Zynvo Style', 'Bags', False, True, False, ''),
            ('Core Casual Tee Men', 'men', 850, 990, 'ZY-MEN-FSN-001', 'Zynvo Style', 'Fashion', False, True, False, ''),
            ('Bright Kids Set', 'kids', 990, 1290, 'ZY-KID-FSN-001', 'Zynvo Style', 'Fashion', False, True, False, ''),
        ]

        for idx, (name, category_key, price, compare_at, sku, brand, group, deal, is_new, trending, badge_text) in enumerate(products, start=1):
            product = Product.objects.filter(sku=sku).first() or Product.objects.filter(name=name).first() or Product(sku=sku)
            product.name = name
            product.sku = sku
            product.category = cats[category_key]
            product.short_description = 'A curated premium pick from Zynvo.'
            product.description = f'{name} is selected to deliver reliable performance, finish, and comfort for everyday use.'
            product.specifications = 'Origin: Bangladesh\nQuality: Premium\nUse: Daily'
            product.price = price
            product.compare_at_price = compare_at
            product.stock = 15 + (idx % 18)
            product.brand = brand
            product.badge_text = badge_text
            product.is_active = True
            product.is_featured = idx % 3 == 0
            product.is_new = is_new
            product.is_daily_deal = deal
            product.is_trending = trending
            product.collection_label = 'Cosmetics Edit' if idx <= 24 else ''
            product.trending_group = group
            product.deal_ends_at = timezone.now() + timedelta(days=3)
            product.meta_title = f'{name} | Zynvo'
            product.meta_description = f'Buy {name} online at Zynvo with fast delivery in Bangladesh.'
            product.save()

            if idx <= 20:
                ProductVariant.objects.update_or_create(
                    product=product,
                    attribute_name='Size',
                    value='Standard',
                    defaults={
                        'sku': f'{sku}-STD',
                        'stock': product.stock,
                        'is_default': True,
                    },
                )
                ProductVariant.objects.update_or_create(
                    product=product,
                    attribute_name='Size',
                    value='Mini',
                    defaults={
                        'sku': f'{sku}-MINI',
                        'stock': max(product.stock - 4, 1),
                        'is_default': False,
                    },
                )

        page_titles = ['about-us', 'contact-us', 'privacy-policy', 'terms-&-conditions', 'return-policy', 'faqs', 'blogs', 'careers']
        for slug in page_titles:
            StaticPage.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': slug.replace('-', ' ').title(),
                    'body': 'This is a demo content page for Zynvo.',
                    'is_published': True,
                },
            )

        blog_cat, _ = BlogCategory.objects.get_or_create(name='Beauty Guides', slug='beauty-guides')
        BlogPost.objects.update_or_create(
            slug='build-a-complete-cosmetics-routine',
            defaults={
                'category': blog_cat,
                'title': 'Build a Complete Cosmetics Routine in 5 Steps',
                'excerpt': 'Choose base, eyes, lips, and skincare prep with balanced formulas.',
                'content': 'This guide helps you choose practical products for office, events, and daily wear while staying within budget.',
                'is_published': True,
            },
        )
        BlogPost.objects.update_or_create(
            slug='how-to-layer-serum-and-moisturizer',
            defaults={
                'category': blog_cat,
                'title': 'How to Layer Serum and Moisturizer for Better Results',
                'excerpt': 'A simple AM/PM method for hydration and glow.',
                'content': 'Use cleanser first, then serum, then moisturizer, and in daytime finish with sunscreen. Keep routines consistent for better outcomes.',
                'is_published': True,
            },
        )

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@zynvo.com', 'admin12345')
            self.stdout.write(self.style.WARNING('Created admin user: admin / admin12345'))

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully with expanded cosmetics catalog.'))
