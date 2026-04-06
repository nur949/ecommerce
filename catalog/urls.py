from django.urls import path

from . import views

urlpatterns = [
    path('shop/', views.shop, name='shop'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/add-to-cart/', views.add_product_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<str:item_key>/', views.remove_cart_item, name='remove_cart_item'),
]
