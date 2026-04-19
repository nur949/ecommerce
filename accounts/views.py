from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import RegisterForm, StyledAuthenticationForm


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
    return render(request, 'accounts/dashboard.html', {'orders': orders})
