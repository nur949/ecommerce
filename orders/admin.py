from django.contrib import admin

from .models import Address, Order, OrderItem, PaymentTransaction


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'sku', 'quantity', 'unit_price', 'total_price')
    can_delete = False


class PaymentInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ('provider', 'reference', 'amount', 'status', 'created_at', 'payload')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'status', 'payment_method', 'payment_status', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_number', 'address__full_name', 'address__phone')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('order_number', 'subtotal', 'discount', 'total', 'created_at')
    list_select_related = ('address', 'user')
    date_hierarchy = 'created_at'
    actions = ('mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled')
    inlines = [OrderItemInline, PaymentInline]

    def customer_name(self, obj):
        return obj.address.full_name if obj.address else 'Guest'

    @admin.action(description='Mark selected orders processing')
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')

    @admin.action(description='Mark selected orders shipped')
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description='Mark selected orders delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')

    @admin.action(description='Mark selected orders cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'city', 'delivery_type', 'created_at')
    list_filter = ('delivery_type', 'city')
    search_fields = ('full_name', 'phone', 'city', 'area')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'order', 'provider', 'amount', 'status', 'created_at')
    list_filter = ('provider', 'status', 'created_at')
    search_fields = ('reference', 'order__order_number')
    list_select_related = ('order',)
