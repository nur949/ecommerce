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


IMG = {
    'lipstick': 'https://images.pexels.com/photos/2533266/pexels-photo-2533266.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'lip_gloss': 'https://images.pexels.com/photos/3373746/pexels-photo-3373746.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'foundation': 'https://images.pexels.com/photos/3373736/pexels-photo-3373736.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'palette': 'https://images.pexels.com/photos/2253834/pexels-photo-2253834.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'mascara': 'https://images.pexels.com/photos/2113855/pexels-photo-2113855.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'brush': 'https://images.pexels.com/photos/2531155/pexels-photo-2531155.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'skincare': 'https://images.pexels.com/photos/6621466/pexels-photo-6621466.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'serum': 'https://images.pexels.com/photos/6724465/pexels-photo-6724465.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'sunscreen': 'https://images.pexels.com/photos/6621461/pexels-photo-6621461.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'haircare': 'https://images.pexels.com/photos/3738348/pexels-photo-3738348.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'perfume': 'https://images.pexels.com/photos/965989/pexels-photo-965989.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'grooming': 'https://images.pexels.com/photos/3992874/pexels-photo-3992874.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'earbuds': 'https://images.pexels.com/photos/3394665/pexels-photo-3394665.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'watch': 'https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'fashion': 'https://images.pexels.com/photos/994523/pexels-photo-994523.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
    'kids': 'https://images.pexels.com/photos/3933030/pexels-photo-3933030.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop',
}


def product(name, category, price, compare, sku, brand, image_key, group, **flags):
    return {
        'name': name,
        'category': category,
        'price': price,
        'compare': compare,
        'sku': sku,
        'brand': brand,
        'image': IMG[image_key],
        'group': group,
        **flags,
    }


class Command(BaseCommand):
    help = 'Recreate realistic demo data for Zynvo'

    def handle(self, *args, **options):
        settings = SiteSettings.load()
        settings.site_name = 'Zynvo'
        settings.tagline = 'Beauty, fashion, and smart essentials in one place.'
        settings.hero_title = 'Real Beauty Picks, Faster Checkout'
        settings.hero_subtitle = 'Shop popular skincare, makeup, fragrance, grooming, fashion, and smart essentials with a modern catalog experience.'
        settings.announcement_text = 'Free delivery on orders over 3000 BDT'
        settings.save()

        self._seed_nav()
        Product.objects.all().delete()
        Category.objects.all().delete()
        HeroSlide.objects.all().delete()
        cats = self._seed_categories()
        self._seed_home_media()
        self._replace_products(cats)
        self._seed_pages_and_blog()
        self._seed_admin()
        self.stdout.write(self.style.SUCCESS('Demo data recreated with real-brand product names, more products, and updated banner imagery.'))

    def _seed_nav(self):
        nav_items = [
            ('Home', '/'),
            ('Makeup', '/category/makeup/'),
            ('Skincare', '/category/skincare/'),
            ('Haircare', '/category/haircare/'),
            ('Fragrance', '/category/fragrance/'),
            ('Men', '/category/men/'),
            ('Fashion', '/category/fashion/'),
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

    def _seed_categories(self):
        category_specs = [
            ('makeup', 'Makeup', None, 1, 'Popular face, lip, eye, and tool picks.', IMG['palette']),
            ('skincare', 'Skincare', None, 2, 'Cleansers, serums, moisturizers, and sun care.', IMG['skincare']),
            ('haircare', 'Haircare', None, 3, 'Shampoo, treatments, oils, and styling essentials.', IMG['haircare']),
            ('fragrance', 'Fragrance', None, 4, 'Women, men, and unisex perfume collections.', IMG['perfume']),
            ('men', 'Men', None, 5, 'Men grooming and lifestyle essentials.', IMG['grooming']),
            ('fashion', 'Fashion', None, 6, 'Bags, apparel, and style accessories.', IMG['fashion']),
            ('kids', 'Kids', None, 7, 'Kids fashion and care picks.', IMG['kids']),
            ('electronics', 'Electronics', None, 8, 'Wearables, audio, and everyday gadgets.', IMG['earbuds']),
            ('lip-makeup', 'Lip Makeup', 'makeup', 1, 'Lipstick, gloss, tint, and liner.', IMG['lipstick']),
            ('face-makeup', 'Face Makeup', 'makeup', 2, 'Foundation, concealer, primer, and blush.', IMG['foundation']),
            ('eye-makeup', 'Eye Makeup', 'makeup', 3, 'Mascara, eyeliner, brow, and palettes.', IMG['mascara']),
            ('beauty-tools', 'Beauty Tools', 'makeup', 4, 'Brushes, sponges, and applicators.', IMG['brush']),
            ('cleanser', 'Cleansers', 'skincare', 1, 'Daily face wash and cleansing balms.', IMG['skincare']),
            ('serum', 'Serums', 'skincare', 2, 'Targeted treatment serums.', IMG['serum']),
            ('moisturizer', 'Moisturizers', 'skincare', 3, 'Cream, gel, and barrier repair moisturizers.', IMG['skincare']),
            ('suncare', 'Sun Care', 'skincare', 4, 'SPF and UV protection products.', IMG['sunscreen']),
            ('hair-wash', 'Hair Wash', 'haircare', 1, 'Shampoo and conditioner.', IMG['haircare']),
            ('hair-treatment', 'Hair Treatments', 'haircare', 2, 'Hair masks, oil, and serum.', IMG['haircare']),
            ('women-perfume', 'Women Perfume', 'fragrance', 1, 'Signature scents for women.', IMG['perfume']),
            ('men-perfume', 'Men Perfume', 'fragrance', 2, 'Daily and evening men fragrances.', IMG['perfume']),
            ('men-grooming', 'Men Grooming', 'men', 1, 'Shaving, beard, and grooming products.', IMG['grooming']),
            ('audio', 'Audio', 'electronics', 1, 'Earbuds, headphones, and speakers.', IMG['earbuds']),
            ('wearables', 'Wearables', 'electronics', 2, 'Smart watches and trackers.', IMG['watch']),
        ]
        cats = {}
        for slug, name, parent_slug, order, description, image_url in category_specs:
            parent = cats.get(parent_slug)
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'parent': parent,
                    'description': description,
                    'external_image_url': image_url,
                    'is_featured': parent is None,
                    'order': order,
                    'meta_title': f'{name} | Zynvo',
                    'meta_description': description,
                },
            )
            cats[slug] = category
        return cats

    def _seed_home_media(self):
        hero_slides = [
            ('Sephora-Inspired Beauty Shelf', 'Shop cult skincare, gloss, mascara, and perfume picks in one fast catalog.', '/category/makeup/', 'New Beauty Drop', 'https://images.pexels.com/photos/3373746/pexels-photo-3373746.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop', '#f8fafc'),
            ('Skincare Routine Refresh', 'Cleanser, niacinamide, barrier cream, and SPF for daily glow.', '/category/skincare/', 'Routine Ready', 'https://images.pexels.com/photos/6621435/pexels-photo-6621435.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop', '#ecfeff'),
            ('Fragrance & Grooming Edit', 'Signature scents and grooming staples for every day.', '/category/fragrance/', 'Long Lasting', 'https://images.pexels.com/photos/965989/pexels-photo-965989.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&fit=crop', '#f5f3ff'),
        ]
        for i, (title, subtitle, url, accent, image_url, color) in enumerate(hero_slides, start=1):
            HeroSlide.objects.update_or_create(
                title=title,
                defaults={
                    'subtitle': subtitle,
                    'cta_text': 'Shop Now',
                    'cta_url': url,
                    'accent_label': accent,
                    'external_image_url': image_url,
                    'bg_color': color,
                    'order': i,
                    'is_active': True,
                },
            )

        banners = [
            ('Lip Gloss Icons', 'Fenty, Maybelline, NYX style picks', '/category/lip-makeup/', '#ffe4ef', 'hero_right', IMG['lip_gloss']),
            ('The Ordinary Routine', 'Serums and barrier care', '/category/skincare/', '#dff7f2', 'hero_right', IMG['serum']),
            ('Signature Perfumes', 'Fresh, floral, woody', '/category/fragrance/', '#efe7ff', 'hero_right', IMG['perfume']),
            ('Brush & Sponge Set', 'Blend faster', '/category/beauty-tools/', '#fce7f3', 'gadget', IMG['brush']),
            ('SPF Bestsellers', 'Daily sun care', '/category/suncare/', '#ecfeff', 'gadget', IMG['sunscreen']),
            ('Hair Repair Shelf', 'Mask, oil, serum', '/category/hair-treatment/', '#fef9c3', 'gadget', IMG['haircare']),
            ('Gloss Bomb Edit', '', '/category/lip-makeup/', '#fbcfe8', 'unlimited', IMG['lip_gloss']),
            ('Niacinamide Serums', '', '/category/serum/', '#d9f99d', 'unlimited', IMG['serum']),
            ('Fragrance Shelf', '', '/category/fragrance/', '#bae6fd', 'unlimited', IMG['perfume']),
            ('Smart Audio Deals', '', '/category/audio/', '#dbeafe', 'unlimited', IMG['earbuds']),
        ]
        PromoBanner.objects.all().delete()
        for i, (title, subtitle, url, color, group, image_url) in enumerate(banners, start=1):
            PromoBanner.objects.create(
                title=title,
                subtitle=subtitle,
                url=url,
                color=color,
                group=group,
                external_image_url=image_url,
                order=i,
                is_active=True,
            )

    def _replace_products(self, cats):
        Product.objects.all().delete()
        now = timezone.now()
        products = [
            product('Fenty Beauty Gloss Bomb Universal Lip Luminizer', 'lip-makeup', 2550, 2990, 'FB-GB-001', 'Fenty Beauty', 'lip_gloss', 'Makeup', is_daily_deal=True, is_trending=True, badge='Cult Pick'),
            product('Maybelline SuperStay Matte Ink Liquid Lipstick', 'lip-makeup', 1150, 1450, 'MNY-SMI-002', 'Maybelline', 'lipstick', 'Makeup', is_new=True, is_trending=True),
            product('NYX Professional Makeup Butter Gloss', 'lip-makeup', 890, 1090, 'NYX-BG-003', 'NYX Professional Makeup', 'lip_gloss', 'Makeup', is_daily_deal=True),
            product('MAC Matte Lipstick Ruby Woo', 'lip-makeup', 2850, 3290, 'MAC-RW-004', 'MAC Cosmetics', 'lipstick', 'Makeup', is_trending=True, badge='Icon'),
            product('Charlotte Tilbury Matte Revolution Pillow Talk', 'lip-makeup', 3650, 4200, 'CT-PT-005', 'Charlotte Tilbury', 'lipstick', 'Makeup', is_new=True),
            product('NARS Radiant Creamy Concealer', 'face-makeup', 3450, 3990, 'NARS-RCC-006', 'NARS', 'foundation', 'Makeup', is_trending=True),
            product('Rare Beauty Soft Pinch Liquid Blush', 'face-makeup', 3150, 3650, 'RB-SPB-007', 'Rare Beauty', 'foundation', 'Makeup', is_daily_deal=True, badge='Trending'),
            product('Maybelline Fit Me Matte + Poreless Foundation', 'face-makeup', 1350, 1690, 'MNY-FIT-008', 'Maybelline', 'foundation', 'Makeup', is_new=True),
            product('e.l.f. Power Grip Primer', 'face-makeup', 1290, 1590, 'ELF-PGP-009', 'e.l.f. Cosmetics', 'foundation', 'Makeup', is_trending=True),
            product('Laura Mercier Translucent Loose Setting Powder', 'face-makeup', 4250, 4890, 'LM-TLP-010', 'Laura Mercier', 'foundation', 'Makeup'),
            product('Too Faced Better Than Sex Mascara', 'eye-makeup', 3150, 3750, 'TF-BTS-011', 'Too Faced', 'mascara', 'Makeup', is_daily_deal=True),
            product('Essence Lash Princess False Lash Effect Mascara', 'eye-makeup', 850, 1050, 'ESS-LP-012', 'essence', 'mascara', 'Makeup', is_trending=True),
            product('Urban Decay Naked3 Eyeshadow Palette', 'eye-makeup', 6250, 6990, 'UD-N3-013', 'Urban Decay', 'palette', 'Makeup', is_new=True),
            product('Anastasia Beverly Hills Brow Wiz', 'eye-makeup', 2750, 3250, 'ABH-BW-014', 'Anastasia Beverly Hills', 'mascara', 'Makeup'),
            product('Real Techniques Everyday Essentials Brush Set', 'beauty-tools', 2450, 2890, 'RT-EE-015', 'Real Techniques', 'brush', 'Makeup', is_daily_deal=True),
            product('Beautyblender Original Makeup Sponge', 'beauty-tools', 2250, 2690, 'BB-ORG-016', 'Beautyblender', 'brush', 'Makeup', is_trending=True),
            product('The Ordinary Niacinamide 10% + Zinc 1%', 'serum', 1350, 1650, 'TO-NIA-017', 'The Ordinary', 'serum', 'Skincare', is_daily_deal=True, is_trending=True, badge='Bestseller'),
            product('The Ordinary Hyaluronic Acid 2% + B5', 'serum', 1450, 1750, 'TO-HA-018', 'The Ordinary', 'serum', 'Skincare', is_new=True),
            product('CeraVe Hydrating Cleanser', 'cleanser', 1850, 2200, 'CRV-HC-019', 'CeraVe', 'skincare', 'Skincare', is_trending=True),
            product('La Roche-Posay Toleriane Purifying Foaming Cleanser', 'cleanser', 2850, 3350, 'LRP-TPC-020', 'La Roche-Posay', 'skincare', 'Skincare'),
            product('COSRX Low pH Good Morning Gel Cleanser', 'cleanser', 1450, 1790, 'COSRX-GM-021', 'COSRX', 'skincare', 'Skincare', is_daily_deal=True),
            product('CeraVe Moisturizing Cream', 'moisturizer', 2350, 2790, 'CRV-MC-022', 'CeraVe', 'skincare', 'Skincare', is_trending=True),
            product('Clinique Moisture Surge 100H Auto-Replenishing Hydrator', 'moisturizer', 4650, 5200, 'CLQ-MS-023', 'Clinique', 'skincare', 'Skincare', is_new=True),
            product('Neutrogena Hydro Boost Water Gel', 'moisturizer', 1850, 2250, 'NEU-HB-024', 'Neutrogena', 'skincare', 'Skincare'),
            product('Supergoop! Unseen Sunscreen SPF 40', 'suncare', 3550, 4100, 'SG-US-025', 'Supergoop!', 'sunscreen', 'Skincare', is_trending=True),
            product('La Roche-Posay Anthelios Melt-In Milk Sunscreen SPF 60', 'suncare', 3290, 3890, 'LRP-AM-026', 'La Roche-Posay', 'sunscreen', 'Skincare', is_daily_deal=True),
            product('Beauty of Joseon Relief Sun Rice + Probiotics SPF50+', 'suncare', 1850, 2290, 'BOJ-RS-027', 'Beauty of Joseon', 'sunscreen', 'Skincare', is_new=True),
            product('Olaplex No.4 Bond Maintenance Shampoo', 'hair-wash', 3250, 3750, 'OLX-N4-028', 'Olaplex', 'haircare', 'Haircare', is_trending=True),
            product('K18 Leave-In Molecular Repair Hair Mask', 'hair-treatment', 6950, 7590, 'K18-MASK-029', 'K18', 'haircare', 'Haircare', is_daily_deal=True),
            product('Moroccanoil Treatment Original', 'hair-treatment', 3850, 4450, 'MO-TO-030', 'Moroccanoil', 'haircare', 'Haircare'),
            product('Dior Sauvage Eau de Parfum', 'men-perfume', 11250, 12490, 'DIOR-SVG-031', 'Dior', 'perfume', 'Fragrance', is_trending=True),
            product('Yves Saint Laurent Libre Eau de Parfum', 'women-perfume', 10850, 11990, 'YSL-LIB-032', 'Yves Saint Laurent', 'perfume', 'Fragrance', is_new=True),
            product('Chanel Coco Mademoiselle Eau de Parfum', 'women-perfume', 13250, 14500, 'CH-CM-033', 'CHANEL', 'perfume', 'Fragrance', is_trending=True, badge='Luxury'),
            product('Versace Dylan Blue Pour Homme', 'men-perfume', 7350, 8290, 'VER-DB-034', 'Versace', 'perfume', 'Fragrance', is_daily_deal=True),
            product('Gillette Fusion5 Razor', 'men-grooming', 1450, 1750, 'GIL-F5-035', 'Gillette', 'grooming', 'Men Grooming'),
            product('Philips Norelco OneBlade Trimmer', 'men-grooming', 4650, 5290, 'PHL-OB-036', 'Philips', 'grooming', 'Men Grooming', is_trending=True),
            product('Sony WF-1000XM5 Wireless Noise Canceling Earbuds', 'audio', 24900, 27900, 'SONY-XM5-037', 'Sony', 'earbuds', 'Audio', is_trending=True),
            product('Apple AirPods Pro 2nd Generation', 'audio', 28500, 31900, 'APL-APP2-038', 'Apple', 'earbuds', 'Audio', is_new=True),
            product('JBL Flip 6 Portable Bluetooth Speaker', 'audio', 11200, 12900, 'JBL-F6-039', 'JBL', 'earbuds', 'Audio', is_daily_deal=True),
            product('Apple Watch SE GPS 40mm', 'wearables', 29900, 33900, 'APL-WSE-040', 'Apple', 'watch', 'Wearables', is_trending=True),
            product('Samsung Galaxy Watch6', 'wearables', 24500, 27900, 'SAM-GW6-041', 'Samsung', 'watch', 'Wearables'),
            product('Nike Heritage Backpack', 'fashion', 3150, 3650, 'NIKE-HB-042', 'Nike', 'fashion', 'Fashion', is_new=True),
            product('Adidas Essentials 3-Stripes Tee', 'fashion', 1850, 2250, 'ADI-TEE-043', 'Adidas', 'fashion', 'Fashion'),
            product('Carter’s Baby 3-Piece Cotton Set', 'kids', 2450, 2890, 'CAR-KID-044', 'Carter’s', 'kids', 'Fashion'),
        ]

        for idx, item in enumerate(products, start=1):
            product_obj = Product.objects.create(
                name=item['name'],
                category=cats[item['category']],
                short_description=f"Popular {item['brand']} item selected for the Zynvo demo catalog.",
                description=(
                    f"{item['name']} is a real-world inspired catalog item. "
                    "Use this demo data to test product cards, filtering, cart, wishlist, checkout, and homepage sections."
                ),
                specifications='Source: public product naming from popular retail/brand catalogs\nDemo image: remote URL\nWarranty: Seller policy applies',
                price=item['price'],
                compare_at_price=item['compare'],
                sku=item['sku'],
                stock=12 + (idx % 22),
                brand=item['brand'],
                badge_text=item.get('badge', ''),
                external_image_url=item['image'],
                is_active=True,
                is_featured=idx % 3 == 0,
                is_new=item.get('is_new', False),
                is_daily_deal=item.get('is_daily_deal', False),
                is_trending=item.get('is_trending', False),
                collection_label='Signature' if idx % 5 == 0 else '',
                trending_group=item['group'],
                deal_ends_at=now + timedelta(days=3 + (idx % 4)),
                meta_title=f"{item['name']} | Zynvo",
                meta_description=f"Buy {item['name']} online at Zynvo with fast delivery in Bangladesh.",
            )
            if idx <= 18:
                ProductVariant.objects.create(
                    product=product_obj,
                    attribute_name='Size',
                    value='Standard',
                    sku=f"{item['sku']}-STD",
                    stock=product_obj.stock,
                    is_default=True,
                )
                ProductVariant.objects.create(
                    product=product_obj,
                    attribute_name='Size',
                    value='Mini / Travel',
                    sku=f"{item['sku']}-MINI",
                    stock=max(product_obj.stock - 5, 1),
                    is_default=False,
                )

    def _seed_pages_and_blog(self):
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
        posts = [
            ('best-cult-beauty-products-to-build-a-routine', 'Best Cult Beauty Products to Build a Routine', 'Start with cleanser, serum, SPF, mascara, and a reliable lip product.'),
            ('how-to-shop-skincare-by-ingredient', 'How to Shop Skincare by Ingredient', 'Niacinamide, hyaluronic acid, ceramides, and SPF solve different daily needs.'),
            ('fragrance-grooming-and-gadget-gift-guide', 'Fragrance, Grooming, and Gadget Gift Guide', 'Easy gifting picks across perfume, trimmer, earbuds, and watch categories.'),
        ]
        for slug, title, excerpt in posts:
            BlogPost.objects.update_or_create(
                slug=slug,
                defaults={
                    'category': blog_cat,
                    'title': title,
                    'excerpt': excerpt,
                    'content': f'{excerpt}\n\nThis demo article supports the modern ecommerce homepage and blog listing.',
                    'is_published': True,
                },
            )

    def _seed_admin(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@zynvo.com', 'admin12345')
            self.stdout.write(self.style.WARNING('Created admin user: admin / admin12345'))
