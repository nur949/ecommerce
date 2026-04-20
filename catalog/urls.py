from django.urls import path

from . import views

urlpatterns = [
    path('shop/', views.shop, name='shop'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/add-to-cart/', views.add_product_to_cart, name='add_to_cart'),
    path('product/<slug:slug>/review/', views.submit_review, name='submit_review'),
    path('product/<slug:slug>/notify-stock/', views.notify_stock, name='notify_stock'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/search/suggest/', views.api_search_suggest, name='api_search_suggest'),
    path('api/products/<slug:slug>/availability/', views.api_product_availability, name='api_product_availability'),
    path('api/products/<slug:slug>/reviews/', views.api_submit_review, name='api_submit_review'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<str:item_key>/', views.remove_cart_item, name='remove_cart_item'),
]
