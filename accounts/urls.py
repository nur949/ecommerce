from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

from .views import UserLoginView, UserLogoutView, add_to_wishlist, dashboard, register_view, remove_from_wishlist, wishlist_view

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.txt',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done'),
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
    path('dashboard/', dashboard, name='dashboard'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<slug:slug>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<slug:slug>/', remove_from_wishlist, name='remove_from_wishlist'),
]
