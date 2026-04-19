from .models import WishlistItem


def account_context(request):
    if not request.user.is_authenticated:
        return {
            'wishlist_count': 0,
            'wishlist_product_ids': set(),
        }

    wishlist_items = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
    wishlist_product_ids = set(wishlist_items)
    return {
        'wishlist_count': len(wishlist_product_ids),
        'wishlist_product_ids': wishlist_product_ids,
    }
