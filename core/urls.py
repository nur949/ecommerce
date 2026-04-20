from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('corporate/', views.corporate, name='corporate'),
    path('outlets/', views.outlets, name='outlets'),
    path('blog/', views.blog_index, name='blog_index'),
    path('blog/demo/<slug:slug>/', views.demo_blog_detail, name='demo_blog_detail'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('pages/<slug:slug>/', views.page_detail, name='page'),
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/homepage-builder/', views.homepage_builder, name='homepage_builder'),
    path('superadmin/seo-dashboard/', views.seo_dashboard, name='seo_dashboard'),
    path('superadmin/seo/product/<int:product_id>/', views.quick_update_product_seo, name='quick_update_product_seo'),
    path('superadmin/seo/category/<int:category_id>/', views.quick_update_category_seo, name='quick_update_category_seo'),
    path('superadmin/seo/page/<int:page_id>/', views.quick_update_page_seo, name='quick_update_page_seo'),
]
