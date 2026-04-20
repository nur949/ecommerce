import json
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils.html import escape
from django.utils import timezone

from catalog.models import Category, Product
from orders.models import Order
from .forms import SearchForm
from .models import BlogPost, HeroSlide, HomeSection, NewsletterSubscriber, PromoBanner, SiteSettings, StaticPage

DEFAULT_HOME_SECTIONS = [
    ('hero', 'Hero Slider'),
    ('hero_showcase', 'Hero Showcase'),
    ('popular_categories', 'Popular Categories'),
    ('daily_deals', 'Daily Deals'),
    ('new_collection', 'New Collection'),
    ('collection_showcase', 'Collection Showcase'),
    ('gadget_banners', 'Gadget Festive'),
    ('trending_now', 'Trending Now'),
    ('unlimited_offer', 'Unlimited Offer'),
    ('corporate_cta', 'Corporate CTA'),
]

CATEGORY_IMAGE_FALLBACKS = [
    (('laptop', 'notebook', 'macbook'), 'https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('desktop', 'pc', 'computer'), 'https://images.pexels.com/photos/704730/pexels-photo-704730.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('phone', 'mobile', 'smartphone', 'iphone'), 'https://images.pexels.com/photos/607812/pexels-photo-607812.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('tablet', 'ipad'), 'https://images.pexels.com/photos/1334597/pexels-photo-1334597.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('camera',), 'https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('monitor', 'display'), 'https://images.pexels.com/photos/777001/pexels-photo-777001.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('gaming', 'game', 'console'), 'https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('headphone', 'earbud', 'audio', 'sound'), 'https://images.pexels.com/photos/3394665/pexels-photo-3394665.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('tv', 'television'), 'https://images.pexels.com/photos/1201996/pexels-photo-1201996.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('appliance', 'kitchen', 'blender', 'mixer', 'oven', 'fridge'), 'https://images.pexels.com/photos/5824519/pexels-photo-5824519.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('network', 'router', 'wifi'), 'https://images.pexels.com/photos/2881229/pexels-photo-2881229.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('security', 'cctv'), 'https://images.pexels.com/photos/430208/pexels-photo-430208.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
    (('accessories', 'gadget', 'component'), 'https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'),
]

DEFAULT_CATEGORY_IMAGE = 'https://images.pexels.com/photos/3945659/pexels-photo-3945659.jpeg?auto=compress&cs=tinysrgb&w=700&h=700&fit=crop'

DEMO_BLOG_POSTS = [
    {
        'slug': 'how-to-pick-the-right-gadget-for-everyday-use',
        'title': 'How to Pick the Right Gadget for Everyday Use',
        'excerpt': 'A practical guide to choosing gadgets by routine, budget, and long-term value.',
        'content': (
            "Choosing a gadget is not only about specs.\n\n"
            "Start with your daily use-case first. If your work depends on video calls, prioritize camera and battery. "
            "If you mostly watch content, focus on display and sound.\n\n"
            "Always compare warranty support and after-sales service before checkout. "
            "A well-supported product usually gives better long-term value."
        ),
        'primary_image_url': 'https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop',
    },
    {
        'slug': 'top-5-smart-home-upgrades-that-save-time',
        'title': 'Top 5 Smart Home Upgrades That Save Time',
        'excerpt': 'From kitchen devices to automation tools, these upgrades make home life faster and easier.',
        'content': (
            "Smart home products are now practical for daily life.\n\n"
            "Start with simple upgrades: smart plugs, lighting routines, and app-connected appliances. "
            "These save time and reduce repetitive tasks.\n\n"
            "Before buying, check compatibility with your current setup and internet reliability."
        ),
        'primary_image_url': 'https://images.pexels.com/photos/5824519/pexels-photo-5824519.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop',
    },
    {
        'slug': 'fast-delivery-safe-payment-what-buyers-should-check',
        'title': 'Fast Delivery, Safe Payment: What Buyers Should Check',
        'excerpt': 'A quick buyer checklist for secure ecommerce orders and reliable delivery.',
        'content': (
            "Safe online shopping depends on a few checks.\n\n"
            "Use trusted payment channels, verify delivery coverage, and read return terms before placing an order.\n\n"
            "Keep your order confirmation and tracking details until delivery is complete."
        ),
        'primary_image_url': 'https://images.pexels.com/photos/6169034/pexels-photo-6169034.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop',
    },
]


def _demo_posts_as_objects():
    posts = []
    for item in DEMO_BLOG_POSTS:
        posts.append(
            SimpleNamespace(
                title=item['title'],
                slug=item['slug'],
                excerpt=item['excerpt'],
                content=item['content'],
                primary_image_url=item['primary_image_url'],
                get_absolute_url=reverse('core:demo_blog_detail', args=[item['slug']]),
            )
        )
    return posts


def ensure_home_sections():
    for index, (key, title) in enumerate(DEFAULT_HOME_SECTIONS):
        HomeSection.objects.get_or_create(key=key, defaults={'title': title, 'order': index})


def get_home_sections():
    ensure_home_sections()
    return HomeSection.objects.order_by('order', 'id')


def get_category_image(category):
    if category.image:
        return category.image.url
    category_name = (category.name or '').lower()
    for keywords, image_url in CATEGORY_IMAGE_FALLBACKS:
        if any(keyword in category_name for keyword in keywords):
            return image_url
    return DEFAULT_CATEGORY_IMAGE


def home(request):
    sections = get_home_sections()
    popular_categories = list(
        Category.objects.filter(is_featured=True, parent__isnull=True)
        .annotate(
            active_product_count=Count('products', filter=Q(products__is_active=True), distinct=True),
            child_count=Count('children', distinct=True),
        )
        .order_by('order', 'name')[:8]
    )
    popular_categories_data = [
        {
            'category': category,
            'image_url': get_category_image(category),
            'product_count': category.active_product_count,
            'child_count': category.child_count,
            'subtitle': category.description[:90] if category.description else 'Curated essentials for daily shopping.',
        }
        for category in popular_categories
    ]
    context = {
        'search_form': SearchForm(request.GET or None),
        'home_sections': sections,
        'hero_slides': HeroSlide.objects.filter(is_active=True),
        'hero_right_banners': PromoBanner.objects.filter(group='hero_right', is_active=True)[:3],
        'popular_categories': popular_categories,
        'popular_categories_data': popular_categories_data,
        'daily_deals': Product.objects.filter(is_active=True, is_daily_deal=True).select_related('category').order_by('-created_at')[:8],
        'new_collection': Product.objects.filter(is_active=True, is_new=True).select_related('category').order_by('-created_at')[:8],
        'collection_showcase': Product.objects.filter(is_active=True, collection_label__iexact='Signature').select_related('category').order_by('-created_at')[:8] or Product.objects.filter(is_active=True, is_featured=True).select_related('category')[:8],
        'gadget_banners': PromoBanner.objects.filter(group='gadget', is_active=True)[:6],
        'unlimited_banners': PromoBanner.objects.filter(group='unlimited', is_active=True)[:4],
        'blog_posts': BlogPost.objects.filter(is_published=True)[:3],
        'deal_now': timezone.now(),
    }
    context['trending_products'] = Product.objects.filter(is_active=True, is_trending=True).select_related('category')[:4] or Product.objects.filter(is_active=True).select_related('category')[:4]
    return render(request, 'core/home.html', context)


@staff_member_required
def superadmin_dashboard(request):
    seo_summary = {
        'products_missing_meta': Product.objects.filter(meta_title='').count() + Product.objects.filter(meta_description='').count(),
        'categories_missing_meta': Category.objects.filter(meta_title='').count() + Category.objects.filter(meta_description='').count(),
        'pages_missing_meta': StaticPage.objects.filter(meta_title='').count() + StaticPage.objects.filter(meta_description='').count(),
    }
    context = {
        'section_count': HomeSection.objects.count(),
        'product_count': Product.objects.count(),
        'category_count': Category.objects.count(),
        'order_count': Order.objects.count(),
        'seo_summary': seo_summary,
        'top_categories': Category.objects.annotate(product_total=Count('products')).order_by('-product_total', 'name')[:6],
    }
    return render(request, 'core/superadmin/dashboard.html', context)


@staff_member_required
def homepage_builder(request):
    ensure_home_sections()
    sections = list(HomeSection.objects.order_by('order', 'id'))
    if request.method == 'POST':
        raw_order = request.POST.get('section_order', '[]')
        active_keys = set(request.POST.getlist('active_keys'))
        try:
            ordered_keys = json.loads(raw_order)
        except json.JSONDecodeError:
            ordered_keys = [section.key for section in sections]
        order_map = {key: index for index, key in enumerate(ordered_keys)}
        for section in sections:
            section.order = order_map.get(section.key, section.order)
            section.is_active = section.key in active_keys
            section.save(update_fields=['order', 'is_active'])
        messages.success(request, 'Homepage builder updated successfully.')
        return redirect('core:homepage_builder')
    return render(request, 'core/superadmin/homepage_builder.html', {'sections': sections})


@staff_member_required
def seo_dashboard(request):
    products = Product.objects.order_by('-updated_at')[:12]
    categories = Category.objects.order_by('name')[:12]
    pages = StaticPage.objects.order_by('title')[:12]
    posts = BlogPost.objects.order_by('-created_at')[:12]
    context = {
        'products': products,
        'categories': categories,
        'pages': pages,
        'posts': posts,
        'products_missing_title': Product.objects.filter(meta_title='').count(),
        'products_missing_description': Product.objects.filter(meta_description='').count(),
        'categories_missing_title': Category.objects.filter(meta_title='').count(),
        'categories_missing_description': Category.objects.filter(meta_description='').count(),
        'pages_missing_title': StaticPage.objects.filter(meta_title='').count(),
        'pages_missing_description': StaticPage.objects.filter(meta_description='').count(),
    }
    return render(request, 'core/superadmin/seo_dashboard.html', context)


@staff_member_required
def quick_update_product_seo(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.meta_title = request.POST.get('meta_title', '').strip()
        product.meta_description = request.POST.get('meta_description', '').strip()
        product.save(update_fields=['meta_title', 'meta_description'])
        messages.success(request, f'SEO updated for {product.name}.')
    return redirect('core:seo_dashboard')


@staff_member_required
def quick_update_category_seo(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.meta_title = request.POST.get('meta_title', '').strip()
        category.meta_description = request.POST.get('meta_description', '').strip()
        category.save(update_fields=['meta_title', 'meta_description'])
        messages.success(request, f'SEO updated for {category.name}.')
    return redirect('core:seo_dashboard')


@staff_member_required
def quick_update_page_seo(request, page_id):
    page = get_object_or_404(StaticPage, pk=page_id)
    if request.method == 'POST':
        page.meta_title = request.POST.get('meta_title', '').strip()
        page.meta_description = request.POST.get('meta_description', '').strip()
        page.save(update_fields=['meta_title', 'meta_description'])
        messages.success(request, f'SEO updated for {page.title}.')
    return redirect('core:seo_dashboard')


def page_detail(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_published=True)
    return render(request, 'core/page_detail.html', {'page': page})


def corporate(request):
    settings = SiteSettings.load()
    return render(request, 'core/corporate.html', {'site_settings': settings})


def outlets(request):
    return render(request, 'core/outlets.html')


def blog_index(request):
    posts = []
    try:
        posts = list(BlogPost.objects.filter(is_published=True))
    except Exception:
        posts = []
    demo_posts = [] if posts else _demo_posts_as_objects()
    return render(request, 'core/blog_index.html', {'posts': posts, 'demo_posts': demo_posts})


def blog_detail(request, slug):
    try:
        post = get_object_or_404(BlogPost, slug=slug, is_published=True)
        return render(request, 'core/blog_detail.html', {'post': post})
    except Exception:
        return demo_blog_detail(request, slug)


def demo_blog_detail(request, slug):
    demo_posts = _demo_posts_as_objects()
    for post in demo_posts:
        if post.slug == slug:
            return render(request, 'core/blog_detail.html', {'post': post})
    raise Http404('Blog post not found.')


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse('core:sitemap_xml'))
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /superadmin/',
        'Disallow: /account/',
        'Disallow: /orders/checkout/',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap_xml(request):
    def add_model_urls(queryset):
        for obj in queryset:
            try:
                urls.append(request.build_absolute_uri(obj.get_absolute_url()))
            except NoReverseMatch:
                continue

    urls = [
        request.build_absolute_uri(reverse('core:home')),
        request.build_absolute_uri(reverse('catalog:shop')),
        request.build_absolute_uri(reverse('core:blog_index')),
        request.build_absolute_uri(reverse('orders:tracking')),
    ]
    add_model_urls(Category.objects.all())
    add_model_urls(Product.objects.filter(is_active=True))
    add_model_urls(StaticPage.objects.filter(is_published=True))
    add_model_urls(BlogPost.objects.filter(is_published=True))
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        body.append(f'  <url><loc>{escape(url)}</loc></url>')
    body.append('</urlset>')
    return HttpResponse('\n'.join(body), content_type='application/xml')


def newsletter_subscribe(request):
    if request.method != 'POST':
        return redirect('core:home')
    email = (request.POST.get('email') or '').strip().lower()
    if not email:
        messages.error(request, 'Please enter a valid email address.')
        return redirect(request.META.get('HTTP_REFERER', reverse('core:home')))
    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email, defaults={'is_active': True})
    if not created and not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save(update_fields=['is_active'])
    messages.success(request, 'Thanks for subscribing to beauty updates.')
    return redirect(request.META.get('HTTP_REFERER', reverse('core:home')))
