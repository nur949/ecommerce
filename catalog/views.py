import json
from decimal import Decimal

from django.contrib import messages
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import cache_page

from orders.cart_utils import (
    add_to_cart,
    build_cart_totals,
    get_cart_coupon,
    get_cart_items,
    get_cart_reward_points,
    remove_from_cart,
    update_cart_quantity,
)

from .models import Category, Product, ProductReview, ProductVariant, StockAlert

PAGE_SIZE = 16


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return None


def _bounded_int(value, default, minimum=1, maximum=None):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = default
    value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value


def _category_tree_ids(category):
    ids = [category.id]
    for child in category.children.all():
        ids.extend(_category_tree_ids(child))
    return ids


def _product_queryset():
    return (
        Product.objects.filter(is_active=True)
        .select_related('category')
        .prefetch_related('variants')
        .annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            review_count=Count('reviews', filter=Q(reviews__is_approved=True)),
        )
    )


def _serialize_product(product):
    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'category': product.category.name if product.category else '',
        'price': str(product.price),
        'compare_at_price': str(product.compare_at_price) if product.compare_at_price else '',
        'discount_percentage': product.discount_percentage,
        'stock': product.stock,
        'in_stock': product.in_stock,
        'ean': product.ean,
        'sku': product.sku,
        'rating': round(product.average_rating or 0, 1),
        'url': product.get_absolute_url(),
        'image': product.primary_image_url,
    }


def _apply_shop_filters(request, products):
    q = (request.GET.get('q') or '').strip()
    category_slug = (request.GET.get('category') or '').strip()
    brand = (request.GET.get('brand') or '').strip()
    rating = request.GET.get('rating') or ''
    min_price = request.GET.get('min_price') or ''
    max_price = request.GET.get('max_price') or ''
    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(brand__icontains=q)
            | Q(sku__icontains=q)
            | Q(ean__icontains=q)
        )
    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            products = products.filter(category_id__in=_category_tree_ids(selected_category))
    if brand:
        products = products.filter(brand__iexact=brand)
    try:
        if rating:
            products = products.filter(reviews__rating__gte=int(rating), reviews__is_approved=True).distinct()
    except (TypeError, ValueError):
        pass
    try:
        if min_price:
            products = products.filter(price__gte=Decimal(min_price))
    except Exception:
        pass
    try:
        if max_price:
            products = products.filter(price__lte=Decimal(max_price))
    except Exception:
        pass
    return products, q, selected_category


def _sort_shop_products(products, sort):
    sort_map = {
        'latest': '-created_at',
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
        'rating': '-average_rating',
    }
    return products.order_by(sort_map.get(sort, '-created_at'))


def _ajax_cart_payload(request):
    cart_items, cart_subtotal = get_cart_items(request)
    cart_count = sum(item['quantity'] for item in cart_items)
    cart_totals = build_cart_totals(
        cart_subtotal,
        coupon=get_cart_coupon(request),
        reward_points=get_cart_reward_points(request),
    )
    mini_cart_html = render_to_string(
        'includes/minicart.html',
        {
            'cart_count': cart_count,
            'cart_items': cart_items,
            'cart_subtotal': cart_subtotal,
            'cart_totals': cart_totals,
        },
        request=request,
    )
    return cart_items, cart_subtotal, cart_count, cart_totals, mini_cart_html


def shop(request):
    if 'sale' in request.GET:
        params = request.GET.copy()
        params.pop('sale', None)
        query_string = params.urlencode()
        next_url = reverse('catalog:shop')
        if query_string:
            next_url = f'{next_url}?{query_string}'
        return redirect(next_url)

    products = _product_queryset()
    products, q, selected_category = _apply_shop_filters(request, products)
    sort = request.GET.get('sort') or 'latest'
    products = _sort_shop_products(products, sort)
    paginator = Paginator(products, PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    brands = sorted(value for value in Product.objects.filter(is_active=True).values_list('brand', flat=True).distinct() if value)
    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': categories,
        'brands': brands,
        'query': q,
        'selected_category': selected_category,
        'selected_brand': (request.GET.get('brand') or '').strip(),
        'selected_rating': (request.GET.get('rating') or '').strip(),
        'min_price': (request.GET.get('min_price') or '').strip(),
        'max_price': (request.GET.get('max_price') or '').strip(),
        'active_sort': sort,
        'product_count': paginator.count,
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'ok': True,
                'html': render_to_string('catalog/partials/product_grid.html', context, request=request),
                'nav_html': render_to_string('catalog/partials/category_nav.html', context, request=request),
                'count': paginator.count,
                'has_next': page_obj.has_next(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            }
        )
    return render(request, 'catalog/shop.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category.objects.prefetch_related('children'), slug=slug)
    products = _product_queryset().filter(category_id__in=_category_tree_ids(category))
    return render(request, 'catalog/category_detail.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category').prefetch_related('gallery', 'variants', 'faqs'), slug=slug, is_active=True)
    related_products = (
        _product_queryset()
        .filter(category=product.category)
        .exclude(id=product.id)[:8]
    )
    selected_variant = product.variants.filter(is_default=True).first() or product.variants.first()
    reviews = product.reviews.filter(is_approved=True).select_related('user')[:10]
    average_rating = product.reviews.filter(is_approved=True).aggregate(value=Avg('rating'))['value'] or 0
    review_count = product.reviews.filter(is_approved=True).count()
    return render(
        request,
        'catalog/product_detail.html',
        {
            'product': product,
            'related_products': related_products,
            'selected_variant': selected_variant,
            'reviews': reviews,
            'average_rating': round(average_rating, 1),
            'review_count': review_count,
        },
    )


def add_product_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variant = None
    variant_id = request.POST.get('variant_id')
    try:
        quantity = int(request.POST.get('quantity', 1) or 1)
    except (TypeError, ValueError):
        quantity = 1
    if variant_id:
        variant = ProductVariant.objects.filter(product=product, id=variant_id).first()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    added_quantity = add_to_cart(request, product, quantity=quantity, variant=variant)

    if is_ajax:
        _, cart_subtotal, cart_count, cart_totals, mini_cart_html = _ajax_cart_payload(request)
        return JsonResponse(
            {
                'ok': True,
                'cart_count': cart_count,
                'cart_subtotal': str(cart_subtotal),
                'cart_totals': {key: str(value) for key, value in cart_totals.items()},
                'mini_cart_html': mini_cart_html,
                'message': f'{product.name} added to cart.' if added_quantity else f'{product.name} is already at the available stock limit.',
            }
        )

    if added_quantity:
        messages.success(request, f'{product.name} added to cart.')
    else:
        messages.info(request, f'{product.name} is already at the available stock limit.')
    next_url = request.POST.get('next') or reverse('catalog:product_detail', args=[slug])
    return redirect(next_url)


def update_cart(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST':
        item_key = request.POST.get('item_key')
        try:
            quantity = int(request.POST.get('quantity', 1) or 1)
        except (TypeError, ValueError):
            quantity = 1
        update_cart_quantity(request, item_key, quantity)
        if is_ajax:
            cart_items, cart_subtotal, cart_count, cart_totals, mini_cart_html = _ajax_cart_payload(request)
            updated_item = next((item for item in cart_items if item['key'] == item_key), None)
            return JsonResponse(
                {
                    'ok': True,
                    'item_key': item_key,
                    'item_total': str(updated_item['total']) if updated_item else '0.00',
                    'item_quantity': updated_item['quantity'] if updated_item else 0,
                    'cart_subtotal': str(cart_subtotal),
                    'cart_totals': {key: str(value) for key, value in cart_totals.items()},
                    'cart_count': cart_count,
                    'mini_cart_html': mini_cart_html,
                }
            )
        messages.success(request, 'Cart updated successfully.')
    return redirect('orders:cart')


@require_POST
def remove_cart_item(request, item_key):
    remove_from_cart(request, item_key)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        _, cart_subtotal, cart_count, cart_totals, mini_cart_html = _ajax_cart_payload(request)
        return JsonResponse(
            {
                'ok': True,
                'item_key': item_key,
                'cart_subtotal': str(cart_subtotal),
                'cart_totals': {key: str(value) for key, value in cart_totals.items()},
                'cart_count': cart_count,
                'mini_cart_html': mini_cart_html,
            }
        )
    messages.info(request, 'Item removed from cart.')
    return redirect(request.META.get('HTTP_REFERER', reverse('orders:cart')))


@require_GET
@cache_page(60)
def api_products(request):
    products = _product_queryset()
    products, _, _ = _apply_shop_filters(request, products)
    sort = request.GET.get('sort') or 'latest'
    products = _sort_shop_products(products, sort)
    paginator = Paginator(products, _bounded_int(request.GET.get('page_size'), 20, maximum=100))
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return JsonResponse(
        {
            'ok': True,
            'count': paginator.count,
            'page': page_obj.number,
            'num_pages': paginator.num_pages,
            'results': [_serialize_product(product) for product in page_obj.object_list],
        }
    )


@require_GET
@cache_page(60 * 10)
def api_categories(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    return JsonResponse(
        {
            'ok': True,
            'results': [
                {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description,
                    'children': [{'id': child.id, 'name': child.name, 'slug': child.slug} for child in category.children.all()],
                }
                for category in categories
            ],
        }
    )


@require_GET
@cache_page(60)
def api_search_suggest(request):
    q = (request.GET.get('q') or '').strip()
    if not q:
        return JsonResponse({'ok': True, 'results': []})
    products = (
        Product.objects.filter(is_active=True)
        .filter(Q(name__icontains=q) | Q(brand__icontains=q) | Q(sku__icontains=q) | Q(ean__icontains=q))
        .order_by('-is_featured', '-created_at')[:8]
    )
    categories = Category.objects.filter(name__icontains=q).order_by('name')[:4]
    return JsonResponse(
        {
            'ok': True,
            'results': [
                {
                    'type': 'product',
                    'label': product.name,
                    'subtext': f'{product.brand} - SKU {product.sku}' + (f' - EAN {product.ean}' if product.ean else ''),
                    'url': product.get_absolute_url(),
                }
                for product in products
            ]
            + [{'type': 'category', 'label': category.name, 'subtext': 'Category', 'url': category.get_absolute_url()} for category in categories],
        }
    )


@require_GET
def api_product_availability(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('variants'), slug=slug, is_active=True)
    return JsonResponse(
        {
            'ok': True,
            'product': {
                'id': product.id,
                'stock': product.stock,
                'in_stock': product.in_stock,
                'is_orderable': product.is_orderable,
            },
            'variants': [{'id': variant.id, 'stock': variant.stock, 'value': variant.value, 'sku': variant.sku} for variant in product.variants.all()],
        }
    )


@require_POST
def submit_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviewer_name = (request.POST.get('reviewer_name') or (request.user.get_full_name() if request.user.is_authenticated else '')).strip()
    reviewer_email = (request.POST.get('reviewer_email') or (request.user.email if request.user.is_authenticated else '')).strip()
    try:
        rating = int(request.POST.get('rating') or 0)
    except (TypeError, ValueError):
        rating = 0
    title = (request.POST.get('title') or '').strip()
    comment = (request.POST.get('comment') or '').strip()
    if not reviewer_name or rating not in {1, 2, 3, 4, 5} or not comment:
        messages.error(request, 'Please provide name, rating and comment to submit your review.')
        return redirect(product.get_absolute_url())
    ProductReview.objects.create(
        product=product,
        user=request.user if request.user.is_authenticated else None,
        reviewer_name=reviewer_name,
        reviewer_email=reviewer_email,
        rating=rating,
        title=title,
        comment=comment,
        is_verified_purchase=request.user.is_authenticated and request.user.order_set.filter(items__product=product).exists(),
    )
    messages.success(request, 'Thanks, your review has been submitted.')
    return redirect(product.get_absolute_url())


@require_POST
def notify_stock(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variant = None
    variant_id = request.POST.get('variant_id')
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product).first()
    email = (request.POST.get('email') or (request.user.email if request.user.is_authenticated else '')).strip()
    if not email:
        messages.error(request, 'Please provide your email to get stock alerts.')
        return redirect(product.get_absolute_url())
    StockAlert.objects.update_or_create(
        product=product,
        variant=variant,
        email=email,
        defaults={'user': request.user if request.user.is_authenticated else None, 'notified': False},
    )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'message': 'We will notify you when this item is back in stock.'})
    messages.success(request, 'We will notify you when this item is back in stock.')
    return redirect(product.get_absolute_url())


@require_POST
def api_submit_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
    rating = _bounded_int(payload.get('rating'), 0, minimum=0, maximum=5)
    reviewer_name = (payload.get('reviewer_name') or '').strip()
    comment = (payload.get('comment') or '').strip()
    if not reviewer_name or rating not in {1, 2, 3, 4, 5} or not comment:
        return JsonResponse({'ok': False, 'error': 'reviewer_name, rating and comment are required.'}, status=400)
    review = ProductReview.objects.create(
        product=product,
        reviewer_name=reviewer_name,
        reviewer_email=(payload.get('reviewer_email') or '').strip(),
        rating=rating,
        title=(payload.get('title') or '').strip(),
        comment=comment,
        is_approved=True,
    )
    return JsonResponse({'ok': True, 'review_id': review.id})
