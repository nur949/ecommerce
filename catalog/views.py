from django.contrib import messages
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Category, Product, ProductVariant
from orders.cart_utils import add_to_cart, get_cart_items, update_cart_quantity, remove_from_cart


def _ajax_cart_payload(request):
    cart_items, cart_subtotal = get_cart_items(request)
    cart_count = sum(item['quantity'] for item in cart_items)
    mini_cart_html = render_to_string(
        'includes/minicart.html',
        {
            'cart_count': cart_count,
            'cart_items': cart_items,
            'cart_subtotal': cart_subtotal,
        },
        request=request,
    )
    return cart_items, cart_subtotal, cart_count, mini_cart_html


def shop(request):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('variants')
    q = (request.GET.get('q') or '').strip()
    if q:
        products = products.filter(name__icontains=q)
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    sale = request.GET.get('sale') in {'1', 'true', 'yes'}
    if sale:
        products = products.filter(compare_at_price__gt=F('price'))
    sort = request.GET.get('sort') or 'latest'
    sort_map = {
        'latest': '-created_at',
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))
    context = {
        'products': products,
        'categories': Category.objects.filter(parent__isnull=True).prefetch_related('children'),
        'query': q,
        'active_category': category_slug or '',
        'active_sort': sort,
        'sale': sale,
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'ok': True,
                'html': render_to_string('catalog/partials/product_grid.html', context, request=request),
                'count': products.count(),
            }
        )
    return render(request, 'catalog/shop.html', {
        **context,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True).select_related('category').prefetch_related('variants')
    return render(request, 'catalog/category_detail.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category').prefetch_related('gallery', 'variants'), slug=slug, is_active=True)
    related_products = Product.objects.select_related('category').filter(category=product.category, is_active=True).exclude(id=product.id)[:8]
    selected_variant = product.variants.filter(is_default=True).first() or product.variants.first()
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'selected_variant': selected_variant,
    })


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
        _, cart_subtotal, cart_count, mini_cart_html = _ajax_cart_payload(request)
        return JsonResponse(
            {
                'ok': True,
                'cart_count': cart_count,
                'cart_subtotal': str(cart_subtotal),
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
            cart_items, cart_subtotal, cart_count, mini_cart_html = _ajax_cart_payload(request)
            updated_item = next((item for item in cart_items if item['key'] == item_key), None)
            return JsonResponse(
                {
                    'ok': True,
                    'item_key': item_key,
                    'item_total': str(updated_item['total']) if updated_item else '0.00',
                    'item_quantity': updated_item['quantity'] if updated_item else 0,
                    'cart_subtotal': str(cart_subtotal),
                    'cart_count': cart_count,
                    'mini_cart_html': mini_cart_html,
                }
            )
        messages.success(request, 'Cart updated successfully.')
    return redirect('orders:cart')


def remove_cart_item(request, item_key):
    remove_from_cart(request, item_key)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        _, cart_subtotal, cart_count, mini_cart_html = _ajax_cart_payload(request)
        return JsonResponse(
            {
                'ok': True,
                'item_key': item_key,
                'cart_subtotal': str(cart_subtotal),
                'cart_count': cart_count,
                'mini_cart_html': mini_cart_html,
            }
        )
    messages.info(request, 'Item removed from cart.')
    return redirect(request.META.get('HTTP_REFERER', reverse('orders:cart')))
