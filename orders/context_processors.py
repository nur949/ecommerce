from .cart_utils import get_cart_items


def cart_context(request):
    items, subtotal = get_cart_items(request)
    return {
        'cart_items': items,
        'cart_subtotal': subtotal,
        'cart_count': sum(item['quantity'] for item in items),
    }
