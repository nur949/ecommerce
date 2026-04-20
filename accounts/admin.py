from django.contrib import admin

from .models import RewardAccount, RewardTransaction, UserProfile, WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'user__email', 'product__name', 'product__sku')
    autocomplete_fields = ('user', 'product')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'birthday', 'marketing_opt_in')
    list_filter = ('marketing_opt_in',)
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(RewardAccount)
class RewardAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'points_balance', 'lifetime_points', 'tier', 'updated_at')
    search_fields = ('user__username', 'user__email')


@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'points', 'reference', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('account__user__username', 'reference', 'reason')
