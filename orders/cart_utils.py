from decimal import Decimal


def _cart(request):
    cart = request.session.get('cart', {})
    request.session['cart'] = cart
    return cart


def make_item_key(product_id, variant_id=None):
    return f'{product_id}:{variant_id or 0}'


def add_to_cart(request, product, quantity=1, variant=None):
    cart = _cart(request)
    key = make_item_key(product.id, variant.id if variant else None)
    if key not in cart:
        cart[key] = {
            'product_id': product.id,
            'variant_id': variant.id if variant else None,
            'quantity': 0,
        }
    cart[key]['quantity'] += max(quantity, 1)
    request.session.modified = True


def update_cart_quantity(request, item_key, quantity):
    cart = _cart(request)
    if item_key in cart:
        if quantity <= 0:
            cart.pop(item_key, None)
        else:
            cart[item_key]['quantity'] = quantity
        request.session.modified = True


def remove_from_cart(request, item_key):
    cart = _cart(request)
    cart.pop(item_key, None)
    request.session.modified = True


def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True


def get_cart_items(request):
    from catalog.models import Product, ProductVariant

    cart = _cart(request)
    items = []
    subtotal = Decimal('0.00')
    for key, entry in cart.items():
        try:
            product = Product.objects.get(id=entry['product_id'], is_active=True)
        except Product.DoesNotExist:
            continue
        variant = None
        unit_price = product.price
        if entry.get('variant_id'):
            variant = ProductVariant.objects.filter(id=entry['variant_id'], product=product).first()
            if variant and variant.price_override:
                unit_price = variant.price_override
        quantity = entry['quantity']
        total = unit_price * quantity
        subtotal += total
        items.append({
            'key': key,
            'product': product,
            'variant': variant,
            'quantity': quantity,
            'unit_price': unit_price,
            'total': total,
        })
    return items, subtotal
