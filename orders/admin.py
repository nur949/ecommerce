from django.contrib import admin

from .models import Address, Order, OrderItem, PaymentTransaction


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'sku', 'quantity', 'unit_price', 'total_price')


class PaymentInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ('provider', 'reference', 'amount', 'status', 'created_at', 'payload')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'status', 'payment_method', 'payment_status', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_number', 'address__full_name', 'address__phone')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('order_number', 'subtotal', 'discount', 'total', 'created_at')
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'city', 'delivery_type', 'created_at')
    search_fields = ('full_name', 'phone', 'city', 'area')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'order', 'provider', 'amount', 'status', 'created_at')
    list_filter = ('provider', 'status', 'created_at')
    search_fields = ('reference', 'order__order_number')
