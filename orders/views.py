import uuid
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart_utils import clear_cart, get_cart_items
from .forms import CheckoutForm, PaymentSelectionForm
from .models import Order, OrderItem, PaymentTransaction


def cart_view(request):
    items, subtotal = get_cart_items(request)
    return render(request, 'orders/cart.html', {'items': items, 'subtotal': subtotal})


def checkout_view(request):
    items, subtotal = get_cart_items(request)
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('catalog:shop')
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            if request.user.is_authenticated:
                address.user = request.user
            address.save()
            discount = Decimal('0.00')
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                address=address,
                order_number=f'ZY{uuid.uuid4().hex[:8].upper()}',
                subtotal=subtotal,
                discount=discount,
                total=subtotal - discount,
                status='awaiting_payment',
                customer_note=request.POST.get('note', ''),
            )
            for item in items:
                variant = item['variant']
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    variant=variant,
                    product_name=item['product'].name,
                    sku=variant.sku if variant and variant.sku else item['product'].sku,
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    total_price=item['total'],
                )
            clear_cart(request)
            messages.success(request, 'Shipping information saved. Choose a payment method to complete your order.')
            return redirect('orders:payment', order_number=order.order_number)
    else:
        initial = {'country': 'Bangladesh'}
        if request.user.is_authenticated:
            initial['full_name'] = request.user.get_full_name() or request.user.username
            initial['phone'] = getattr(request.user, 'profile_phone', '') or ''
            initial['city'] = 'Dhaka'
        form = CheckoutForm(initial=initial)
    return render(request, 'orders/checkout.html', {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'discount': Decimal('0.00'),
        'total': subtotal,
    })


def payment_view(request, order_number):
    order = get_object_or_404(Order.objects.select_related('address'), order_number=order_number)
    if request.method == 'POST':
        form = PaymentSelectionForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['payment_method']
            order.payment_method = method
            provider_map = {
                'cod': 'Cash on Delivery',
                'bkash': 'bKash Sandbox',
                'card': 'Stripe Sandbox',
                'bank': 'Bank Transfer',
            }
            tx = PaymentTransaction.objects.create(
                order=order,
                provider=provider_map[method],
                reference=f'TX{uuid.uuid4().hex[:10].upper()}',
                amount=order.total,
                status='pending' if method in {'bkash', 'bank'} else 'initiated',
                payload={
                    'mobile_number': form.cleaned_data.get('mobile_number', ''),
                    'transaction_id': form.cleaned_data.get('transaction_id', ''),
                    'cardholder_name': form.cleaned_data.get('cardholder_name', ''),
                },
            )
            if method == 'cod':
                order.payment_status = 'unpaid'
                order.status = 'confirmed'
                tx.status = 'success'
                tx.save(update_fields=['status'])
            elif method == 'card':
                order.payment_status = 'paid'
                order.status = 'confirmed'
                tx.status = 'success'
                tx.save(update_fields=['status'])
            else:
                order.payment_status = 'pending'
                order.status = 'pending'
            order.save(update_fields=['payment_method', 'payment_status', 'status'])
            messages.success(request, f'Payment method saved for order {order.order_number}.')
            return redirect('orders:payment_complete', order_number=order.order_number)
    else:
        form = PaymentSelectionForm(initial={'payment_method': order.payment_method})
    return render(request, 'orders/payment.html', {'order': order, 'form': form})


def payment_complete(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('payments', 'items'), order_number=order_number)
    return render(request, 'orders/payment_complete.html', {'order': order, 'latest_payment': order.payments.first()})


def order_detail(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items', 'payments'), order_number=order_number)
    return render(request, 'orders/order_detail.html', {'order': order, 'latest_payment': order.payments.first()})


def order_tracking(request):
    order = None
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        order = Order.objects.filter(order_number__iexact=order_number).first()
        if not order:
            messages.error(request, 'No order found with that tracking number.')
    return render(request, 'orders/order_tracking.html', {'order': order})
