import json
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from catalog.models import Product
from orders.cart_utils import add_to_cart
from orders.models import Address, Cart, CartItem, Order

from .forms import AccountPasswordChangeForm, AddressForm, ProfileForm, RegisterForm, StyledAuthenticationForm
from .models import UserProfile, WishlistItem
from .services import get_or_create_reward_account, maybe_grant_birthday_offer

User = get_user_model()


def _token_secret():
    return settings.SECRET_KEY


def _create_jwt_for_user(user):
    now = datetime.utcnow()
    payload = {
        'sub': str(user.id),
        'username': user.username,
        'iat': now,
        'exp': now + timedelta(days=7),
    }
    return jwt.encode(payload, _token_secret(), algorithm='HS256')


def _get_bearer_user(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ', 1)[1].strip()
    if not token:
        return None
    try:
        payload = jwt.decode(token, _token_secret(), algorithms=['HS256'])
        return User.objects.filter(id=payload.get('sub')).first()
    except jwt.PyJWTError:
        return None


def _require_bearer_user(request):
    return _get_bearer_user(request)


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return None


class UserLoginView(LoginView):
    template_name = 'accounts/login_register.html'
    authentication_form = StyledAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_form'] = RegisterForm()
        context['active_tab'] = 'login'
        return context


class UserLogoutView(LogoutView):
    pass


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            phone = form.cleaned_data.get('phone', '')
            if phone:
                UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
            get_or_create_reward_account(user)
            login(request, user)
            messages.success(request, 'Your account was created successfully.')
            return redirect('accounts:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/login_register.html', {
        'form': StyledAuthenticationForm(),
        'register_form': form,
        'active_tab': 'register',
    })


@login_required
def dashboard(request):
    maybe_grant_birthday_offer(request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'profile':
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated.')
                return redirect('accounts:dashboard')
            messages.error(request, 'Please fix the profile form errors.')
        elif action == 'password':
            password_form = AccountPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed.')
                return redirect('accounts:dashboard')
            messages.error(request, 'Please fix the password form errors.')
        elif action == 'delete_account':
            request.user.delete()
            messages.info(request, 'Your account has been deleted.')
            return redirect('core:home')
    orders = request.user.order_set.select_related('address').prefetch_related('items').all()[:10]
    addresses = request.user.addresses.all()
    wishlist_items = request.user.wishlist_items.select_related('product', 'product__category')[:8]
    reward_account = get_or_create_reward_account(request.user)
    reward_transactions = reward_account.transactions.all()[:5]
    profile_form = locals().get('profile_form') or ProfileForm(instance=profile, user=request.user)
    password_form = locals().get('password_form') or AccountPasswordChangeForm(request.user)
    address_form = AddressForm()
    return render(
        request,
        'accounts/dashboard.html',
        {
            'orders': orders,
            'addresses': addresses,
            'wishlist_items': wishlist_items,
            'reward_account': reward_account,
            'reward_transactions': reward_transactions,
            'profile': profile,
            'profile_form': profile_form,
            'password_form': password_form,
            'address_form': address_form,
        },
    )


@login_required
def wishlist_view(request):
    wishlist_items = request.user.wishlist_items.select_related('product', 'product__category').all()
    return render(request, 'accounts/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
@require_POST
def move_wishlist_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    add_to_cart(request, product, quantity=1)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'{product.name} moved to cart.')
    return redirect(request.POST.get('next') or reverse('accounts:wishlist'))


@login_required
@require_POST
def address_create(request):
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        if not request.user.addresses.exists():
            address.is_default = True
        address.save()
        messages.success(request, 'Address saved.')
    else:
        messages.error(request, 'Please fix the address form errors.')
    return redirect('accounts:dashboard')


@login_required
@require_POST
def address_update(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    form = AddressForm(request.POST, instance=address)
    if form.is_valid():
        form.save()
        messages.success(request, 'Address updated.')
    else:
        messages.error(request, 'Please fix the address form errors.')
    return redirect('accounts:dashboard')


@login_required
@require_POST
def address_delete(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    was_default = address.is_default
    address.delete()
    if was_default:
        next_address = request.user.addresses.first()
        if next_address:
            next_address.is_default = True
            next_address.save(update_fields=['is_default'])
    messages.info(request, 'Address deleted.')
    return redirect('accounts:dashboard')


@login_required
@require_POST
def address_set_default(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save(update_fields=['is_default'])
    messages.success(request, 'Default address updated.')
    return redirect('accounts:dashboard')


@login_required
@require_POST
def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    _, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'ok': True,
                'product_id': product.id,
                'is_wishlisted': True,
                'wishlist_count': wishlist_count,
                'add_url': reverse('accounts:add_to_wishlist', args=[product.slug]),
                'remove_url': reverse('accounts:remove_from_wishlist', args=[product.slug]),
                'message': f'{product.name} added to your wishlist.' if created else f'{product.name} is already in your wishlist.',
            }
        )
    if created:
        messages.success(request, f'{product.name} added to your wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('catalog:product_detail', args=[slug]))


@login_required
@require_POST
def remove_from_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    deleted, _ = WishlistItem.objects.filter(user=request.user, product=product).delete()
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'ok': True,
                'product_id': product.id,
                'is_wishlisted': False,
                'wishlist_count': wishlist_count,
                'add_url': reverse('accounts:add_to_wishlist', args=[product.slug]),
                'remove_url': reverse('accounts:remove_from_wishlist', args=[product.slug]),
                'message': f'{product.name} removed from your wishlist.' if deleted else f'{product.name} was not in your wishlist.',
            }
        )
    if deleted:
        messages.info(request, f'{product.name} removed from your wishlist.')
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('accounts:wishlist'))


@csrf_exempt
@require_POST
def api_register(request):
    payload = _json_body(request)
    if payload is None:
        return HttpResponseBadRequest('Invalid JSON payload.')
    password = payload.get('password') or ''
    email = (payload.get('email') or '').strip().lower()
    first_name = (payload.get('name') or payload.get('first_name') or '').strip()
    if not password or not email:
        return JsonResponse({'ok': False, 'error': 'email and password are required.'}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'ok': False, 'error': 'Email already exists.'}, status=400)
    user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name)
    UserProfile.objects.update_or_create(user=user, defaults={'phone': (payload.get('phone') or '').strip()})
    get_or_create_reward_account(user)
    token = _create_jwt_for_user(user)
    return JsonResponse({'ok': True, 'token': token, 'user': _serialize_user(user)})


@csrf_exempt
@require_POST
def api_login(request):
    payload = _json_body(request)
    if payload is None:
        return HttpResponseBadRequest('Invalid JSON payload.')
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password') or ''
    user_lookup = User.objects.filter(email__iexact=email).only('username').first()
    username = user_lookup.username if user_lookup else email
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Invalid credentials.'}, status=401)
    token = _create_jwt_for_user(user)
    return JsonResponse({'ok': True, 'token': token, 'user': _serialize_user(user)})


def _serialize_user(user):
    profile = getattr(user, 'profile', None)
    return {
        'id': user.id,
        'name': user.get_full_name() or user.first_name or user.username,
        'email': user.email,
        'avatar': profile.avatar.url if profile and profile.avatar else '',
        'phone': profile.phone if profile else '',
        'created_at': user.date_joined.isoformat(),
    }


def _serialize_address(address):
    return {
        'id': address.id,
        'address_line': address.address_line,
        'street': address.address_line,
        'city': address.city,
        'area': address.area,
        'postal_code': address.postcode,
        'is_default': address.is_default,
    }


def _serialize_order(order):
    return {
        'id': order.id,
        'order_number': order.order_number,
        'total_price': str(order.total),
        'status': order.status,
        'created_at': order.created_at.isoformat(),
        'products': [
            {
                'product_name': item.product_name,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'total_price': str(item.total_price),
            }
            for item in order.items.all()
        ],
    }


def _serialize_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    items = cart.items.select_related('product', 'variant')
    return {
        'id': cart.id,
        'items': [
            {
                'product_id': item.product_id,
                'variant_id': item.variant_id,
                'name': item.product.name,
                'quantity': item.quantity,
                'unit_price': str(item.variant.price_override if item.variant and item.variant.price_override else item.product.price),
                'key': item.key,
            }
            for item in items
        ],
    }


def _add_product_to_user_cart(user, product, quantity=1, variant=None):
    cart, _ = Cart.objects.get_or_create(user=user)
    quantity = max(int(quantity or 1), 1)
    available_stock = variant.stock if variant else product.stock
    if available_stock <= 0:
        return False
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=variant, defaults={'quantity': 0})
    item.quantity = min((0 if created else item.quantity) + quantity, available_stock)
    item.save(update_fields=['quantity', 'updated_at'])
    return True


@csrf_exempt
def api_profile(request):
    user = _get_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    reward_account = get_or_create_reward_account(user)
    if request.method == 'GET':
        return JsonResponse(
            {
                'ok': True,
                'profile': {
                    **_serialize_user(user),
                    'birthday': profile.birthday.isoformat() if profile.birthday else '',
                    'beauty_preferences': profile.beauty_preferences,
                    'preferred_brands': profile.preferred_brands,
                    'marketing_opt_in': profile.marketing_opt_in,
                    'reward_points': reward_account.points_balance,
                    'reward_tier': reward_account.tier,
                },
            }
        )
    if request.method != 'PATCH':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    payload = _json_body(request)
    if payload is None:
        return HttpResponseBadRequest('Invalid JSON payload.')
    if 'name' in payload or 'first_name' in payload:
        user.first_name = (payload.get('name') or payload.get('first_name') or '').strip()
    if 'email' in payload:
        email = (payload.get('email') or '').strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            return JsonResponse({'ok': False, 'error': 'Email already exists.'}, status=400)
        user.email = email
        user.username = email
    user.save(update_fields=['first_name', 'email', 'username'])
    if 'phone' in payload:
        profile.phone = (payload.get('phone') or '').strip()
    if 'birthday' in payload:
        birthday_raw = (payload.get('birthday') or '').strip()
        if birthday_raw:
            try:
                profile.birthday = datetime.strptime(birthday_raw, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'ok': False, 'error': 'Birthday must be in YYYY-MM-DD format.'}, status=400)
        else:
            profile.birthday = None
    if 'beauty_preferences' in payload:
        profile.beauty_preferences = (payload.get('beauty_preferences') or '').strip()
    if 'preferred_brands' in payload:
        profile.preferred_brands = (payload.get('preferred_brands') or '').strip()
    if 'marketing_opt_in' in payload:
        profile.marketing_opt_in = bool(payload.get('marketing_opt_in'))
    profile.save()
    return JsonResponse({'ok': True, 'user': _serialize_user(user)})


@csrf_exempt
def api_addresses(request):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    if request.method == 'GET':
        return JsonResponse({'ok': True, 'addresses': [_serialize_address(address) for address in user.addresses.all()]})
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
    address = Address.objects.create(
        user=user,
        full_name=(payload.get('full_name') or user.get_full_name() or user.email).strip(),
        phone=(payload.get('phone') or getattr(getattr(user, 'profile', None), 'phone', '')).strip(),
        city=(payload.get('city') or '').strip(),
        area=(payload.get('area') or '').strip(),
        address_line=(payload.get('address_line') or payload.get('street') or '').strip(),
        postcode=(payload.get('postal_code') or payload.get('postcode') or '').strip(),
        is_default=bool(payload.get('is_default')) or not user.addresses.exists(),
    )
    return JsonResponse({'ok': True, 'address': _serialize_address(address)}, status=201)


@csrf_exempt
def api_address_detail(request, address_id):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    address = get_object_or_404(Address, id=address_id, user=user)
    if request.method == 'PATCH':
        payload = _json_body(request)
        if payload is None:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
        field_map = {
            'city': 'city',
            'area': 'area',
            'address_line': 'address_line',
            'street': 'address_line',
            'postal_code': 'postcode',
            'postcode': 'postcode',
        }
        for source, target in field_map.items():
            if source in payload:
                setattr(address, target, (payload.get(source) or '').strip())
        if 'is_default' in payload:
            address.is_default = bool(payload.get('is_default'))
        address.save()
        return JsonResponse({'ok': True, 'address': _serialize_address(address)})
    if request.method == 'DELETE':
        address.delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


@require_GET
def api_orders(request):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    orders = user.order_set.select_related('address').prefetch_related('items').all()
    return JsonResponse({'ok': True, 'orders': [_serialize_order(order) for order in orders]})


@require_GET
def api_order_detail(request, order_number):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number, user=user)
    return JsonResponse({'ok': True, 'order': _serialize_order(order)})


@csrf_exempt
def api_wishlist(request):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    if request.method == 'GET':
        items = user.wishlist_items.select_related('product')
        return JsonResponse(
            {
                'ok': True,
                'items': [
                    {
                        'id': item.id,
                        'product_id': item.product_id,
                        'name': item.product.name,
                        'price': str(item.product.price),
                        'image': item.product.primary_image_url,
                        'url': item.product.get_absolute_url(),
                    }
                    for item in items
                ],
            }
        )
    if request.method == 'POST':
        payload = _json_body(request)
        if payload is None:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
        product = get_object_or_404(Product, id=payload.get('product_id'), is_active=True)
        item, _ = WishlistItem.objects.get_or_create(user=user, product=product)
        return JsonResponse({'ok': True, 'id': item.id}, status=201)
    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_wishlist_detail(request, product_id):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    if request.method == 'DELETE':
        WishlistItem.objects.filter(user=user, product_id=product_id).delete()
        return JsonResponse({'ok': True})
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        _add_product_to_user_cart(user, product, quantity=1)
        WishlistItem.objects.filter(user=user, product=product).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_cart(request):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    if request.method == 'GET':
        return JsonResponse({'ok': True, 'cart': _serialize_cart(user)})
    if request.method == 'POST':
        payload = _json_body(request)
        if payload is None:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
        product = get_object_or_404(Product, id=payload.get('product_id'), is_active=True)
        variant = None
        if payload.get('variant_id'):
            variant = get_object_or_404(product.variants, id=payload.get('variant_id'))
        quantity = max(int(payload.get('quantity') or 1), 1)
        if not _add_product_to_user_cart(user, product, quantity=quantity, variant=variant):
            return JsonResponse({'ok': False, 'error': 'Product is out of stock.'}, status=400)
        return JsonResponse({'ok': True, 'cart': _serialize_cart(user)}, status=201)
    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_cart_item(request, product_id):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    cart, _ = Cart.objects.get_or_create(user=user)
    variant_id = request.GET.get('variant_id') or None
    item = get_object_or_404(CartItem.objects.select_related('product', 'variant'), cart=cart, product_id=product_id, variant_id=variant_id)
    if request.method == 'PATCH':
        payload = _json_body(request)
        if payload is None:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)
        quantity = max(int(payload.get('quantity') or 1), 1)
        available_stock = item.variant.stock if item.variant else item.product.stock
        item.quantity = min(quantity, available_stock)
        item.save(update_fields=['quantity', 'updated_at'])
        return JsonResponse({'ok': True, 'cart': _serialize_cart(user)})
    if request.method == 'DELETE':
        item.delete()
        return JsonResponse({'ok': True, 'cart': _serialize_cart(user)})
    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


@require_GET
def api_dashboard(request):
    user = _require_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    reward_account = get_or_create_reward_account(user)
    orders = user.order_set.order_by('-created_at')[:10]
    return JsonResponse(
        {
            'ok': True,
            'user': _serialize_user(user),
            'orders': [_serialize_order(order) for order in orders],
            'rewards': {
                'points_balance': reward_account.points_balance,
                'lifetime_points': reward_account.lifetime_points,
                'tier': reward_account.tier,
                'transactions': [
                    {
                        'type': tx.transaction_type,
                        'points': tx.points,
                        'reason': tx.reason,
                        'created_at': tx.created_at.isoformat(),
                    }
                    for tx in reward_account.transactions.all()[:8]
                ],
            },
            'wishlist_count': user.wishlist_items.count(),
        }
    )
