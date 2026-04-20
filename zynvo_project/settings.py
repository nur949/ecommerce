import os
import sys
from pathlib import Path

import dj_database_url
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
IS_TEST = 'test' in sys.argv
IS_RUNSERVER = 'runserver' in sys.argv

debug_env = os.getenv('DEBUG')
if debug_env is None:
    DEBUG = True
else:
    DEBUG = debug_env.lower() in {'1', 'true', 'yes', 'on'}
if IS_TEST:
    DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = get_random_secret_key()

default_allowed_hosts = '127.0.0.1,localhost,testserver,.onrender.com'
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', default_allowed_hosts).split(',') if host.strip()]

default_csrf_origins = ''
if not DEBUG:
    default_csrf_origins = 'https://*.onrender.com'
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', default_csrf_origins).split(',')
    if origin.strip()
]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'catalog',
    'accounts',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zynvo_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_context',
                'accounts.context_processors.account_context',
                'orders.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'zynvo_project.wsgi.application'

database_url = os.getenv('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(
        default=database_url or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=not DEBUG if database_url else False,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

JAZZMIN_SETTINGS = {
    'site_title': 'Zynvo Admin',
    'site_header': 'Zynvo',
    'site_brand': 'Zynvo',
    'welcome_sign': 'Commerce Analytics',
    'copyright': 'Zynvo',
    'show_sidebar': True,
    'navigation_expanded': False,
    'hide_apps': [],
    'hide_models': [
        'auth.Group',
        'sessions.Session',
    ],
    'order_with_respect_to': [
        'auth.User',
        'orders.Order',
        'catalog.Product',
        'orders.Cart',
        'accounts.UserProfile',
        'accounts.WishlistItem',
    ],
    'icons': {
        'auth.User': 'fas fa-users',
        'accounts.UserProfile': 'fas fa-id-card',
        'accounts.WishlistItem': 'fas fa-heart',
        'orders.Order': 'fas fa-box',
        'orders.Cart': 'fas fa-shopping-bag',
        'orders.Address': 'fas fa-map-marker-alt',
        'orders.Coupon': 'fas fa-ticket-alt',
        'catalog.Product': 'fas fa-tags',
        'catalog.Category': 'fas fa-layer-group',
        'core.SiteSettings': 'fas fa-sliders-h',
        'core.HeroSlide': 'fas fa-images',
    },
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'darkly',
    'default_theme_mode': 'dark',
    'navbar': 'navbar-dark',
    'sidebar': 'sidebar-dark-primary',
    'brand_colour': 'navbar-dark',
    'accent': 'accent-teal',
    'button_classes': {
        'primary': 'btn btn-primary',
        'secondary': 'btn btn-outline-light',
        'success': 'btn btn-success',
        'danger': 'btn btn-danger',
        'warning': 'btn btn-warning',
        'info': 'btn btn-info',
    },
    'actions_sticky_top': True,
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '1209600'))
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = (
    os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in {'1', 'true', 'yes', 'on'}
    and not DEBUG
    and not IS_TEST
    and not IS_RUNSERVER
)

if not DEBUG and not IS_RUNSERVER:
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
PAYMENT_SANDBOX_MODE = os.getenv('PAYMENT_SANDBOX_MODE', 'True').lower() in {'1', 'true', 'yes', 'on'}
DASHBOARD_STATS_CACHE_SECONDS = int(os.getenv('DASHBOARD_STATS_CACHE_SECONDS', '60'))
DASHBOARD_STATS_RATE_LIMIT = int(os.getenv('DASHBOARD_STATS_RATE_LIMIT', '60'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console'],
            'level': os.getenv('ORDER_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
