from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('', include(('catalog.urls', 'catalog'), namespace='catalog')),
    path('account/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('profile/', include(('profiles.urls', 'profiles'), namespace='profiles')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
