from decimal import Decimal


def _cart(request, create=False):
    cart = request.session.get('cart')
    if cart is None:
        cart = {}
        if create:
            request.session['cart'] = cart
    return cart


def make_item_key(product_id, variant_id=None):
    return f'{product_id}:{variant_id or 0}'


def add_to_cart(request, product, quantity=1, variant=None):
    cart = _cart(request, create=True)
    key = make_item_key(product.id, variant.id if variant else None)
    requested_quantity = max(int(quantity or 1), 1)
    available_stock = variant.stock if variant else product.stock
    available_stock = max(int(available_stock or 0), 0)
    if available_stock <= 0:
        return 0
    current_quantity = int(cart.get(key, {}).get('quantity', 0))
    next_quantity = current_quantity + requested_quantity
    if available_stock:
        next_quantity = min(next_quantity, available_stock)
    if key not in cart:
        cart[key] = {
            'product_id': product.id,
            'variant_id': variant.id if variant else None,
            'quantity': 0,
        }
    cart[key]['quantity'] = next_quantity
    request.session.modified = True
    return next_quantity - current_quantity


def update_cart_quantity(request, item_key, quantity):
    cart = _cart(request, create=True)
    if item_key in cart:
        if quantity <= 0:
            cart.pop(item_key, None)
        else:
            next_quantity = max(int(quantity or 1), 1)
            entry = cart[item_key]
            try:
                from catalog.models import Product, ProductVariant

                product = Product.objects.get(id=entry['product_id'], is_active=True)
                variant = None
                if entry.get('variant_id'):
                    variant = ProductVariant.objects.filter(id=entry['variant_id'], product=product).first()
                available_stock = variant.stock if variant else product.stock
                available_stock = max(int(available_stock or 0), 0)
                if available_stock <= 0:
                    cart.pop(item_key, None)
                else:
                    cart[item_key]['quantity'] = min(next_quantity, available_stock)
            except Product.DoesNotExist:
                cart.pop(item_key, None)
        request.session.modified = True


def remove_from_cart(request, item_key):
    cart = _cart(request, create=True)
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
    if not cart:
        return items, subtotal

    product_ids = [entry.get('product_id') for entry in cart.values() if entry.get('product_id')]
    variant_ids = [entry.get('variant_id') for entry in cart.values() if entry.get('variant_id')]
    products = Product.objects.filter(id__in=product_ids, is_active=True).select_related('category').in_bulk()
    variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product').in_bulk()
    stale_keys = []

    for key, entry in cart.items():
        product = products.get(entry.get('product_id'))
        if not product:
            stale_keys.append(key)
            continue
        variant = None
        unit_price = product.price
        if entry.get('variant_id'):
            variant = variants.get(entry['variant_id'])
            if variant and variant.product_id != product.id:
                variant = None
            if variant and variant.price_override:
                unit_price = variant.price_override
        quantity = max(int(entry.get('quantity') or 1), 1)
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
    for key in stale_keys:
        cart.pop(key, None)
    if stale_keys:
        request.session.modified = True
    return items, subtotal
