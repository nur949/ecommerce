from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CartApiView,
    CartItemApiView,
    CategoryListApiView,
    LoginApiView,
    ProductDetailApiView,
    ProductListApiView,
    ProductReviewListCreateApiView,
    RegisterApiView,
    WishlistApiView,
    WishlistDetailApiView,
)

urlpatterns = [
    path('auth/register/', RegisterApiView.as_view(), name='api-register'),
    path('auth/login/', LoginApiView.as_view(), name='api-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('categories/', CategoryListApiView.as_view(), name='api-categories'),
    path('products/', ProductListApiView.as_view(), name='api-products'),
    path('products/<slug:slug>/', ProductDetailApiView.as_view(), name='api-product-detail'),
    path('products/<slug:slug>/reviews/', ProductReviewListCreateApiView.as_view(), name='api-product-reviews'),
    path('wishlist/', WishlistApiView.as_view(), name='api-wishlist'),
    path('wishlist/<int:product_id>/', WishlistDetailApiView.as_view(), name='api-wishlist-detail'),
    path('cart/', CartApiView.as_view(), name='api-cart'),
    path('cart/<str:item_key>/', CartItemApiView.as_view(), name='api-cart-item'),
]
