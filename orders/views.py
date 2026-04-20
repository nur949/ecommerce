import json
import uuid
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from accounts.services import add_reward_points, get_or_create_reward_account, redeem_reward_points
from catalog.models import ProductVariant

from .cart_utils import (
    build_cart_totals,
    clear_cart,
    get_cart_coupon,
    get_cart_items,
    get_cart_reward_points,
    set_cart_coupon,
    set_cart_reward_points,
)
from .forms import CheckoutForm, PaymentSelectionForm
from .models import Coupon, Order, OrderItem, PaymentTransaction


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return None


def _remember_order_access(request, order_number):
    recent_orders = request.session.get('recent_order_numbers', [])
    recent_orders = [value for value in recent_orders if value != order_number]
    recent_orders.insert(0, order_number)
    request.session['recent_order_numbers'] = recent_orders[:5]
    request.session.modified = True


def _can_access_order(request, order):
    if request.user.is_staff:
        return True
    if request.user.is_authenticated:
        return order.user_id == request.user.id
    return order.order_number in request.session.get('recent_order_numbers', [])


def _get_accessible_order(request, order_number, *, include_payments=False):
    queryset = Order.objects.select_related('address').prefetch_related('items')
    if include_payments:
        queryset = queryset.prefetch_related('payments')
    order = get_object_or_404(queryset, order_number=order_number)
    if not _can_access_order(request, order):
        raise Http404('Order not found.')
    return order


def _reserve_stock_for_items(items):
    from catalog.models import Product

    for item in items:
        product = Product.objects.select_for_update().get(pk=item['product'].pk)
        variant = None
        stock_label = product.name
        if item['variant']:
            variant = ProductVariant.objects.select_for_update().get(pk=item['variant'].pk)
            stock_label = f'{product.name} ({variant.value})'
            available_stock = variant.stock
        else:
            available_stock = product.stock

        if available_stock < item['quantity']:
            raise ValueError(f'Only {available_stock} unit(s) available for {stock_label}.')

        if variant:
            variant.stock -= item['quantity']
            variant.save(update_fields=['stock'])
        product.stock = max(product.stock - item['quantity'], 0)
        product.save(update_fields=['stock'])


def _reward_earn_points(total_amount):
    return int(Decimal(total_amount or 0) // Decimal('100'))


def cart_view(request):
    items, subtotal = get_cart_items(request)
    if request.method == 'POST':
        coupon_code = (request.POST.get('coupon_code') or '').strip()
        reward_points = request.POST.get('reward_points')
        if 'remove_coupon' in request.POST:
            set_cart_coupon(request, '')
            messages.info(request, 'Coupon removed.')
        elif coupon_code:
            coupon = set_cart_coupon(request, coupon_code)
            if coupon:
                messages.success(request, f'Coupon {coupon.code} applied.')
            else:
                messages.error(request, 'Invalid or expired coupon code.')
        if reward_points is not None:
            set_cart_reward_points(request, reward_points)
            messages.success(request, 'Reward points updated.')
        return redirect('orders:cart')
    coupon = get_cart_coupon(request)
    reward_points = get_cart_reward_points(request)
    if request.user.is_authenticated:
        reward_account = get_or_create_reward_account(request.user)
        reward_points = min(reward_points, reward_account.points_balance)
        set_cart_reward_points(request, reward_points)
    else:
        reward_account = None
        if reward_points:
            set_cart_reward_points(request, 0)
            reward_points = 0
    totals = build_cart_totals(subtotal, coupon=coupon, reward_points=reward_points)
    return render(
        request,
        'orders/cart.html',
        {
            'items': items,
            'subtotal': subtotal,
            'coupon': coupon,
            'totals': totals,
            'reward_points': reward_points,
            'reward_account': reward_account,
        },
    )


def checkout_view(request):
    items, subtotal = get_cart_items(request)
    coupon = get_cart_coupon(request)
    reward_points = get_cart_reward_points(request)
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('catalog:shop')
    if request.user.is_authenticated:
        reward_account = get_or_create_reward_account(request.user)
        reward_points = min(reward_points, reward_account.points_balance)
    else:
        reward_account = None
        reward_points = 0
    totals = build_cart_totals(subtotal, coupon=coupon, reward_points=reward_points)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    address = form.save(commit=False)
                    if request.user.is_authenticated:
                        address.user = request.user
                    address.save()
                    _reserve_stock_for_items(items)
                    order = Order.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        address=address,
                        order_number=f'ZY{uuid.uuid4().hex[:8].upper()}',
                        subtotal=totals['subtotal'],
                        discount=totals['discount_total'],
                        total=totals['total'],
                        coupon_code=coupon.code if coupon else '',
                        reward_points_used=reward_points if request.user.is_authenticated else 0,
                        reward_points_earned=_reward_earn_points(totals['total']) if request.user.is_authenticated else 0,
                        status='awaiting_payment',
                        customer_note=request.POST.get('note', '').strip(),
                    )
                    order_items = []
                    for item in items:
                        variant = item['variant']
                        order_items.append(
                            OrderItem(
                                order=order,
                                product=item['product'],
                                variant=variant,
                                product_name=item['product'].name,
                                sku=variant.sku if variant and variant.sku else item['product'].sku,
                                quantity=item['quantity'],
                                unit_price=item['unit_price'],
                                total_price=item['total'],
                            )
                        )
                    OrderItem.objects.bulk_create(order_items)
                    if request.user.is_authenticated and reward_points:
                        redeem_reward_points(request.user, reward_points, reason='Checkout redemption', reference=order.order_number)
            except ValueError as exc:
                messages.error(request, str(exc))
            else:
                clear_cart(request)
                _remember_order_access(request, order.order_number)
                messages.success(request, 'Shipping information saved. Choose a payment method to complete your order.')
                return redirect('orders:payment', order_number=order.order_number)
    else:
        initial = {'country': 'Bangladesh'}
        if request.user.is_authenticated:
            initial['full_name'] = request.user.get_full_name() or request.user.username
            initial['phone'] = getattr(getattr(request.user, 'profile', None), 'phone', '') or ''
            initial['city'] = 'Dhaka'
        form = CheckoutForm(initial=initial)
    return render(
        request,
        'orders/checkout.html',
        {
            'form': form,
            'items': items,
            'subtotal': totals['subtotal'],
            'discount': totals['discount_total'],
            'total': totals['total'],
            'coupon': coupon,
            'reward_points': reward_points,
            'reward_account': reward_account,
            'totals': totals,
        },
    )


def payment_view(request, order_number):
    order = _get_accessible_order(request, order_number, include_payments=True)
    if request.method == 'POST' and order.payments.exists():
        messages.info(request, f'Payment has already been recorded for order {order.order_number}.')
        return redirect('orders:payment_complete', order_number=order.order_number)
    if request.method == 'POST':
        form = PaymentSelectionForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['payment_method']
            order.payment_method = method
            provider_map = {
                'cod': 'Cash on Delivery',
                'bkash': 'bKash Sandbox',
                'stripe': 'Stripe',
                'paypal': 'PayPal',
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
            if method in {'cod', 'stripe', 'paypal'}:
                order.payment_status = 'paid' if method in {'stripe', 'paypal'} else 'unpaid'
                order.status = 'confirmed'
                tx.status = 'success'
                tx.save(update_fields=['status'])
            else:
                order.payment_status = 'pending'
                order.status = 'pending'
            order.save(update_fields=['payment_method', 'payment_status', 'status'])
            if order.user_id and order.status == 'confirmed' and order.reward_points_earned > 0:
                add_reward_points(
                    order.user,
                    order.reward_points_earned,
                    reason=f'Order reward for {order.order_number}',
                    reference=order.order_number,
                )
            messages.success(request, f'Payment method saved for order {order.order_number}.')
            return redirect('orders:payment_complete', order_number=order.order_number)
    else:
        form = PaymentSelectionForm(initial={'payment_method': order.payment_method})
    return render(request, 'orders/payment.html', {'order': order, 'form': form})


def payment_complete(request, order_number):
    order = _get_accessible_order(request, order_number, include_payments=True)
    return render(request, 'orders/payment_complete.html', {'order': order, 'latest_payment': order.payments.first()})


def order_detail(request, order_number):
    order = _get_accessible_order(request, order_number, include_payments=True)
    return render(request, 'orders/order_detail.html', {'order': order, 'latest_payment': order.payments.first()})


def order_tracking(request):
    order = None
    if request.method == 'POST':
        order_number = (request.POST.get('order_number') or '').strip()
        if not order_number:
            messages.error(request, 'Please enter your order number before tracking.')
            return render(request, 'orders/order_tracking.html', {'order': None})
        order = Order.objects.select_related('address').filter(order_number__iexact=order_number).first()
        if not order:
            messages.error(request, 'No order found with that tracking number.')
    return render(request, 'orders/order_tracking.html', {'order': order})


@require_POST
def api_coupon_validate(request):
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
    code = (payload.get('code') or '').strip().upper()
    try:
        subtotal = Decimal(str(payload.get('subtotal') or '0'))
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid subtotal.'}, status=400)
    coupon = Coupon.objects.filter(code__iexact=code, is_active=True).first()
    if not coupon:
        return JsonResponse({'ok': False, 'error': 'Coupon not found.'}, status=404)
    discount = build_cart_totals(subtotal, coupon=coupon, reward_points=0)['coupon_discount']
    if discount <= 0:
        return JsonResponse({'ok': False, 'error': 'Coupon is not applicable for current subtotal.'}, status=400)
    return JsonResponse({'ok': True, 'coupon': {'code': coupon.code, 'discount': str(discount)}})


@require_GET
def api_order_status(request, order_number):
    order = _get_accessible_order(request, order_number, include_payments=True)
    return JsonResponse(
        {
            'ok': True,
            'order_number': order.order_number,
            'status': order.status,
            'payment_status': order.payment_status,
            'total': str(order.total),
            'discount': str(order.discount),
            'coupon_code': order.coupon_code,
            'reward_points_used': order.reward_points_used,
            'reward_points_earned': order.reward_points_earned,
            'items': [
                {
                    'product_name': item.product_name,
                    'sku': item.sku,
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'total_price': str(item.total_price),
                }
                for item in order.items.all()
            ],
            'transactions': [
                {
                    'provider': tx.provider,
                    'reference': tx.reference,
                    'status': tx.status,
                    'amount': str(tx.amount),
                    'created_at': tx.created_at.isoformat(),
                }
                for tx in order.payments.all()
            ],
        }
    )


@require_GET
def api_cart_summary(request):
    items, subtotal = get_cart_items(request)
    coupon = get_cart_coupon(request)
    reward_points = get_cart_reward_points(request)
    totals = build_cart_totals(subtotal, coupon=coupon, reward_points=reward_points)
    return JsonResponse(
        {
            'ok': True,
            'count': sum(item['quantity'] for item in items),
            'coupon': coupon.code if coupon else '',
            'reward_points': reward_points,
            'totals': {k: str(v) for k, v in totals.items()},
            'items': [
                {
                    'key': item['key'],
                    'product_id': item['product'].id,
                    'product_name': item['product'].name,
                    'variant_id': item['variant'].id if item['variant'] else None,
                    'quantity': item['quantity'],
                    'unit_price': str(item['unit_price']),
                    'total': str(item['total']),
                }
                for item in items
            ],
        }
    )


@login_required
@require_POST
def api_order_status_update(request, order_number):
    if not request.user.is_staff:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=403)
    order = get_object_or_404(Order, order_number=order_number)
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
    next_status = (payload.get('status') or '').strip()
    if next_status not in dict(Order.STATUS_CHOICES):
        return JsonResponse({'ok': False, 'error': 'Invalid status'}, status=400)
    order.status = next_status
    order.save(update_fields=['status'])
    return JsonResponse({'ok': True, 'order_number': order.order_number, 'status': order.status})
