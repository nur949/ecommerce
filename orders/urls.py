from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<str:order_number>/', views.payment_view, name='payment'),
    path('payment/<str:order_number>/complete/', views.payment_complete, name='payment_complete'),
    path('tracking/', views.order_tracking, name='tracking'),
    path('api/cart/summary/', views.api_cart_summary, name='api_cart_summary'),
    path('api/coupons/validate/', views.api_coupon_validate, name='api_coupon_validate'),
    path('api/orders/<str:order_number>/status/', views.api_order_status, name='api_order_status'),
    path('api/orders/<str:order_number>/status/update/', views.api_order_status_update, name='api_order_status_update'),
    path('<str:order_number>/', views.order_detail, name='detail'),
]
