import json
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from catalog.models import Product

from .forms import RegisterForm, StyledAuthenticationForm
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
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
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
    orders = request.user.order_set.select_related('address').prefetch_related('items').all()[:8]
    wishlist_items = request.user.wishlist_items.select_related('product', 'product__category')[:4]
    reward_account = get_or_create_reward_account(request.user)
    reward_transactions = reward_account.transactions.all()[:5]
    profile = getattr(request.user, 'profile', None)
    return render(
        request,
        'accounts/dashboard.html',
        {
            'orders': orders,
            'wishlist_items': wishlist_items,
            'reward_account': reward_account,
            'reward_transactions': reward_transactions,
            'profile': profile,
        },
    )


@login_required
def wishlist_view(request):
    wishlist_items = request.user.wishlist_items.select_related('product', 'product__category').all()
    return render(request, 'accounts/wishlist.html', {'wishlist_items': wishlist_items})


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
    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    email = (payload.get('email') or '').strip().lower()
    first_name = (payload.get('first_name') or '').strip()
    if not username or not password or not email:
        return JsonResponse({'ok': False, 'error': 'username, email and password are required.'}, status=400)
    if User.objects.filter(username__iexact=username).exists():
        return JsonResponse({'ok': False, 'error': 'Username already exists.'}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'ok': False, 'error': 'Email already exists.'}, status=400)
    user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
    get_or_create_reward_account(user)
    token = _create_jwt_for_user(user)
    return JsonResponse({'ok': True, 'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email}})


@csrf_exempt
@require_POST
def api_login(request):
    payload = _json_body(request)
    if payload is None:
        return HttpResponseBadRequest('Invalid JSON payload.')
    username = (payload.get('username') or payload.get('email') or '').strip()
    password = payload.get('password') or ''
    if '@' in username:
        user_lookup = User.objects.filter(email__iexact=username).only('username').first()
        if user_lookup:
            username = user_lookup.username
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Invalid credentials.'}, status=401)
    token = _create_jwt_for_user(user)
    return JsonResponse({'ok': True, 'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email}})


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
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'phone': profile.phone,
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
    for field in ['first_name', 'email']:
        if field in payload:
            setattr(user, field, (payload.get(field) or '').strip())
    user.save(update_fields=['first_name', 'email'])
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
    return JsonResponse({'ok': True})


@require_GET
def api_dashboard(request):
    user = request.user if request.user.is_authenticated else _get_bearer_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    reward_account = get_or_create_reward_account(user)
    orders = user.order_set.order_by('-created_at')[:10]
    return JsonResponse(
        {
            'ok': True,
            'orders': [
                {
                    'order_number': order.order_number,
                    'status': order.status,
                    'payment_status': order.payment_status,
                    'total': str(order.total),
                    'created_at': order.created_at.isoformat(),
                }
                for order in orders
            ],
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
