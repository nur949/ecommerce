from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Category, Product, ProductVariant
from orders.cart_utils import add_to_cart, get_cart_items, update_cart_quantity, remove_from_cart


def shop(request):
    products = Product.objects.filter(is_active=True)
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(request, 'catalog/shop.html', {'products': products, 'categories': Category.objects.all(), 'query': q or ''})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    return render(request, 'catalog/category_detail.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('gallery', 'variants'), slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:8]
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
    quantity = int(request.POST.get('quantity', 1) or 1)
    if variant_id:
        variant = ProductVariant.objects.filter(product=product, id=variant_id).first()
    add_to_cart(request, product, quantity=quantity, variant=variant)
    messages.success(request, f'{product.name} added to cart.')
    next_url = request.POST.get('next') or reverse('catalog:product_detail', args=[slug])
    return redirect(next_url)


def update_cart(request):
    if request.method == 'POST':
        item_key = request.POST.get('item_key')
        quantity = int(request.POST.get('quantity', 1) or 1)
        update_cart_quantity(request, item_key, quantity)
        messages.success(request, 'Cart updated successfully.')
    return redirect('orders:cart')


def remove_cart_item(request, item_key):
    remove_from_cart(request, item_key)
    messages.info(request, 'Item removed from cart.')
    return redirect(request.META.get('HTTP_REFERER', reverse('orders:cart')))
