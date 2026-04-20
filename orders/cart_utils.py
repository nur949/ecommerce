from decimal import Decimal

from django.utils import timezone

from .models import Cart, CartItem, Coupon

FREE_DELIVERY_THRESHOLD = Decimal('3000.00')


def _cart(request, create=False):
    cart = request.session.get('cart')
    if cart is None:
        cart = {}
        if create:
            request.session['cart'] = cart
    return cart


def _user_cart(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return None
    cart, _ = Cart.objects.get_or_create(user=request.user)
    session_cart = request.session.get('cart') or {}
    if session_cart:
        from catalog.models import Product, ProductVariant

        product_ids = [entry.get('product_id') for entry in session_cart.values() if entry.get('product_id')]
        variant_ids = [entry.get('variant_id') for entry in session_cart.values() if entry.get('variant_id')]
        products = Product.objects.filter(id__in=product_ids, is_active=True).in_bulk()
        variants = ProductVariant.objects.filter(id__in=variant_ids).in_bulk()
        for entry in session_cart.values():
            product = products.get(entry.get('product_id'))
            if not product:
                continue
            variant = variants.get(entry.get('variant_id')) if entry.get('variant_id') else None
            quantity = max(int(entry.get('quantity') or 1), 1)
            item, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=variant, defaults={'quantity': quantity})
            if not created:
                item.quantity = max(item.quantity, quantity)
                item.save(update_fields=['quantity', 'updated_at'])
        request.session['cart'] = {}
        request.session.modified = True
    return cart


def make_item_key(product_id, variant_id=None):
    return f'{product_id}:{variant_id or 0}'


def add_to_cart(request, product, quantity=1, variant=None):
    user_cart = _user_cart(request)
    cart = _cart(request, create=True)
    key = make_item_key(product.id, variant.id if variant else None)
    requested_quantity = max(int(quantity or 1), 1)
    available_stock = variant.stock if variant else product.stock
    available_stock = max(int(available_stock or 0), 0)
    if available_stock <= 0:
        return 0
    if user_cart:
        item, _ = CartItem.objects.get_or_create(cart=user_cart, product=product, variant=variant, defaults={'quantity': 0})
        current_quantity = int(item.quantity or 0)
        next_quantity = min(current_quantity + requested_quantity, available_stock)
        item.quantity = next_quantity
        item.save(update_fields=['quantity', 'updated_at'])
        return next_quantity - current_quantity
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
    user_cart = _user_cart(request)
    if user_cart:
        try:
            product_id, variant_id = item_key.split(':', 1)
            variant_id = None if variant_id == '0' else int(variant_id)
            item = CartItem.objects.select_related('product', 'variant').get(cart=user_cart, product_id=int(product_id), variant_id=variant_id)
        except (ValueError, CartItem.DoesNotExist):
            return
        if quantity <= 0:
            item.delete()
            return
        available_stock = item.variant.stock if item.variant else item.product.stock
        available_stock = max(int(available_stock or 0), 0)
        if available_stock <= 0:
            item.delete()
            return
        item.quantity = min(max(int(quantity or 1), 1), available_stock)
        item.save(update_fields=['quantity', 'updated_at'])
        return
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
    user_cart = _user_cart(request)
    if user_cart:
        try:
            product_id, variant_id = item_key.split(':', 1)
            variant_id = None if variant_id == '0' else int(variant_id)
        except ValueError:
            return
        CartItem.objects.filter(cart=user_cart, product_id=product_id, variant_id=variant_id).delete()
        return
    cart = _cart(request, create=True)
    cart.pop(item_key, None)
    request.session.modified = True


def clear_cart(request):
    user_cart = _user_cart(request)
    if user_cart:
        user_cart.items.all().delete()
    request.session['cart'] = {}
    request.session.pop('cart_coupon_code', None)
    request.session.pop('cart_reward_points', None)
    request.session.modified = True


def get_cart_items(request):
    from catalog.models import Product, ProductVariant

    user_cart = _user_cart(request)
    if user_cart:
        items = []
        subtotal = Decimal('0.00')
        stale_ids = []
        cart_items = user_cart.items.select_related('product', 'variant', 'product__category')
        for cart_item in cart_items:
            product = cart_item.product
            if not product.is_active:
                stale_ids.append(cart_item.id)
                continue
            variant = cart_item.variant
            unit_price = variant.price_override if variant and variant.price_override else product.price
            quantity = max(int(cart_item.quantity or 1), 1)
            available_stock = variant.stock if variant else product.stock
            available_stock = max(int(available_stock or 0), 0)
            if available_stock <= 0:
                stale_ids.append(cart_item.id)
                continue
            if quantity > available_stock:
                quantity = available_stock
                cart_item.quantity = quantity
                cart_item.save(update_fields=['quantity', 'updated_at'])
            total = unit_price * quantity
            subtotal += total
            items.append({
                'key': cart_item.key,
                'product': product,
                'variant': variant,
                'quantity': quantity,
                'unit_price': unit_price,
                'total': total,
            })
        if stale_ids:
            CartItem.objects.filter(id__in=stale_ids).delete()
        return items, subtotal

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
        available_stock = variant.stock if variant else product.stock
        available_stock = max(int(available_stock or 0), 0)
        if available_stock <= 0:
            stale_keys.append(key)
            continue
        if quantity > available_stock:
            quantity = available_stock
            entry['quantity'] = quantity
            request.session.modified = True
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


def set_cart_coupon(request, code):
    code = (code or '').strip().upper()
    if not code:
        request.session.pop('cart_coupon_code', None)
        request.session.modified = True
        return None
    coupon = Coupon.objects.filter(code__iexact=code, is_active=True).first()
    if not coupon:
        return None
    now = timezone.now()
    if coupon.starts_at and coupon.starts_at > now:
        return None
    if coupon.ends_at and coupon.ends_at < now:
        return None
    request.session['cart_coupon_code'] = coupon.code
    request.session.modified = True
    return coupon


def get_cart_coupon(request):
    code = request.session.get('cart_coupon_code')
    if not code:
        return None
    coupon = Coupon.objects.filter(code__iexact=code, is_active=True).first()
    if not coupon:
        request.session.pop('cart_coupon_code', None)
        request.session.modified = True
        return None
    now = timezone.now()
    if (coupon.starts_at and coupon.starts_at > now) or (coupon.ends_at and coupon.ends_at < now):
        request.session.pop('cart_coupon_code', None)
        request.session.modified = True
        return None
    return coupon


def set_cart_reward_points(request, points):
    try:
        points = int(points or 0)
    except (TypeError, ValueError):
        points = 0
    request.session['cart_reward_points'] = max(points, 0)
    request.session.modified = True


def get_cart_reward_points(request):
    try:
        points = int(request.session.get('cart_reward_points') or 0)
    except (TypeError, ValueError):
        request.session.pop('cart_reward_points', None)
        request.session.modified = True
        return 0
    return max(points, 0)


def calculate_discount(subtotal, coupon=None):
    subtotal = Decimal(subtotal or 0)
    if not coupon:
        return Decimal('0.00')
    if subtotal < coupon.min_subtotal:
        return Decimal('0.00')
    if coupon.discount_type == 'percent':
        discount = (subtotal * coupon.discount_value) / Decimal('100')
    else:
        discount = coupon.discount_value
    if coupon.max_discount_amount:
        discount = min(discount, coupon.max_discount_amount)
    return max(min(discount, subtotal), Decimal('0.00'))


def build_cart_totals(subtotal, coupon=None, reward_points=0):
    subtotal = Decimal(subtotal or 0)
    coupon_discount = calculate_discount(subtotal, coupon)
    try:
        reward_points = int(reward_points or 0)
    except (TypeError, ValueError):
        reward_points = 0
    reward_discount = min(Decimal(max(reward_points, 0)), max(subtotal - coupon_discount, Decimal('0.00')))
    total_discount = coupon_discount + reward_discount
    total = max(subtotal - total_discount, Decimal('0.00'))
    free_delivery_remaining = max(FREE_DELIVERY_THRESHOLD - subtotal, Decimal('0.00'))
    return {
        'subtotal': subtotal,
        'coupon_discount': coupon_discount,
        'reward_discount': reward_discount,
        'discount_total': total_discount,
        'total': total,
        'free_delivery_threshold': FREE_DELIVERY_THRESHOLD,
        'free_delivery_remaining': free_delivery_remaining,
    }
