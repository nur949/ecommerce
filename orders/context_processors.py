from .cart_utils import build_cart_totals, get_cart_coupon, get_cart_items, get_cart_reward_points


def cart_context(request):
    items, subtotal = get_cart_items(request)
    coupon = get_cart_coupon(request)
    reward_points = get_cart_reward_points(request)
    totals = build_cart_totals(subtotal, coupon=coupon, reward_points=reward_points)
    return {
        'cart_items': items,
        'cart_subtotal': subtotal,
        'cart_count': sum(item['quantity'] for item in items),
        'cart_coupon': coupon,
        'cart_reward_points': reward_points,
        'cart_totals': totals,
    }
