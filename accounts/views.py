from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import RegisterForm, StyledAuthenticationForm
from .models import WishlistItem
from catalog.models import Product


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
    orders = request.user.order_set.select_related('address').prefetch_related('items').all()[:5]
    wishlist_items = request.user.wishlist_items.select_related('product', 'product__category')[:4]
    return render(request, 'accounts/dashboard.html', {'orders': orders, 'wishlist_items': wishlist_items})


@login_required
def wishlist_view(request):
    wishlist_items = request.user.wishlist_items.select_related('product', 'product__category').all()
    return render(request, 'accounts/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    _, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'{product.name} added to your wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('catalog:product_detail', args=[slug]))


@login_required
def remove_from_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    deleted, _ = WishlistItem.objects.filter(user=request.user, product=product).delete()
    if deleted:
        messages.info(request, f'{product.name} removed from your wishlist.')
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('accounts:wishlist'))
