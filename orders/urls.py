from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<str:order_number>/', views.payment_view, name='payment'),
    path('payment/<str:order_number>/complete/', views.payment_complete, name='payment_complete'),
    path('tracking/', views.order_tracking, name='tracking'),
    path('<str:order_number>/', views.order_detail, name='detail'),
]
