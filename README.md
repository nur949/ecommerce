# Zynvo - Modern Django Ecommerce Platform

Zynvo is a production-ready **Django ecommerce website** built with **Django 6**, **Django templates**, **Tailwind CSS**, **Bootstrap 5**, and modular **Fetch API JavaScript**. It is designed for a fast, SEO-friendly online store with SPA-like interactions while keeping Django's clean MVT architecture.

This project includes product catalog management, AJAX cart updates, wishlist, user accounts, profile dashboard, checkout, payment flow, order tracking, blog/CMS pages, admin analytics, demo data seeding, and Render deployment configuration.

**Keywords:** Django ecommerce, Python ecommerce website, Django online store, Tailwind ecommerce template, Django shopping cart, AJAX cart Django, Django wishlist, Django user profile, Django SEO website, Django Render deployment.

## Live Demo

[View Live Demo](https://ecommerce-1-pp7c.onrender.com)

## Repository

[GitHub Repository](https://github.com/nur949/ecommerce)

## Table of Contents

- [Project Highlights](#project-highlights)
- [Core Features](#core-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Demo Data](#demo-data)
- [Admin Access](#admin-access)
- [SEO Features](#seo-features)
- [AJAX and SPA-Like UX](#ajax-and-spa-like-ux)
- [Deployment](#deployment)
- [Testing](#testing)
- [Useful Commands](#useful-commands)

## Project Highlights

- **Django 6 ecommerce project** with modular apps and clean MVT structure.
- **SEO-friendly server-rendered pages** with fast AJAX enhancements.
- **Modern SaaS-style UI** using Tailwind CSS and Bootstrap utilities.
- **SPA-like shopping experience** without React, Vue, or a heavy frontend framework.
- **Realistic demo catalog** with real-brand style product names and remote product/banner images.
- **Production-ready settings** for static files, security headers, PostgreSQL, Gunicorn, WhiteNoise, and Render.

## Core Features

### Ecommerce Catalog

- Product listing page with search, category, brand, rating, price, and sorting filters.
- Product detail pages with gallery, variants, stock status, SKU, price, reviews, FAQ, and related products.
- Product categories and nested category navigation.
- Product variants for size/options.
- Product badges, compare-at price, discounts, daily deals, trending products, and new arrivals.
- Lazy-loaded product images.

### Cart and Checkout

- AJAX add to cart.
- AJAX cart quantity update.
- AJAX cart item remove.
- Live cart icon count update.
- Mini cart drawer with dynamic totals.
- Cart subtotal, coupon discount, reward discount, free delivery progress, and final total.
- Checkout address form.
- Payment selection flow with demo methods:
  - Cash on Delivery
  - bKash / mobile banking style payment
  - Stripe-style card flow
  - PayPal
  - Bank transfer

### Wishlist

- Authenticated wishlist system.
- AJAX wishlist add/remove toggle.
- Live wishlist badge update.
- Move wishlist item to cart.

### User Authentication

- User registration.
- Login and logout.
- Password reset templates.
- Password change from dashboard.
- Django built-in authentication system.

### User Profile System

- Dedicated `profiles` app.
- `UserProfile` model linked to Django `User` with `OneToOneField`.
- Profile fields:
  - profile picture
  - bio
  - phone
  - address
  - website
- Auto profile creation with Django signals.
- Profile overview page.
- Profile edit page.
- Modern dashboard-style profile UI.

### Account Dashboard

- Personal profile update.
- Avatar upload.
- Birthday, beauty preferences, preferred brands, marketing opt-in.
- Address management.
- Recent orders.
- Wishlist summary.
- Rewards summary.
- Password change.
- Account deletion flow.

### CMS and SEO Content

- Blog index and blog detail pages.
- Static pages:
  - About
  - Contact
  - Privacy Policy
  - Terms and Conditions
  - Return Policy
  - FAQs
- Dynamic sitemap XML.
- Robots.txt.
- Meta titles and descriptions for products, categories, pages, and posts.

### Admin and Analytics

- Django admin with Jazzmin UI.
- Admin dashboard stats API.
- Revenue, orders, users, recent activity, and operational logs.
- Homepage section builder.
- SEO dashboard for quick meta updates.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 6 |
| Architecture | Django MVT, modular apps |
| Database | SQLite for local development, PostgreSQL for production |
| Frontend | Django Templates, HTML, Tailwind CSS, Bootstrap 5 |
| JavaScript | Fetch API, modular vanilla JS |
| Auth | Django built-in auth |
| Admin | Django Admin, Jazzmin |
| Static Files | WhiteNoise |
| Deployment | Render, Gunicorn |
| Images | Local media uploads and external demo image URLs |
| API | Django `JsonResponse`, AJAX endpoints |

## Project Structure

```text
ecommerce/
├── accounts/              # Auth, account dashboard, wishlist, account APIs
├── catalog/               # Categories, products, variants, reviews, shop filters
├── core/                  # Homepage, CMS pages, blog, SEO, admin dashboard, seed data
├── orders/                # Cart, checkout, payment, orders, coupons
├── profiles/              # Dedicated user profile system
├── static/
│   ├── css/               # Global styles
│   ├── js/                # main.js, api.js, ui.js
│   └── img/               # Default avatar and static assets
├── templates/
│   ├── accounts/          # Login, register, dashboard, password templates
│   ├── catalog/           # Shop, product detail, product partials
│   ├── core/              # Homepage, blog, CMS, superadmin templates
│   ├── orders/            # Cart, checkout, payment, tracking
│   ├── profiles/          # Profile overview and edit pages
│   └── includes/          # Header, footer, minicart
├── zynvo_project/         # Django settings, URLs, WSGI/ASGI
├── media/                 # Uploaded media files
├── manage.py
├── requirements.txt
├── render.yaml
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/nur949/ecommerce.git
cd ecommerce
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:

```powershell
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed demo data

```bash
python manage.py seed_demo
```

### 7. Start development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Environment Variables

The project works locally without custom environment variables. For production, configure:

```env
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DB_NAME
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_AGE=1209600
DASHBOARD_STATS_CACHE_SECONDS=60
DASHBOARD_STATS_RATE_LIMIT=60
```

Payment placeholders:

```env
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
PAYMENT_SANDBOX_MODE=True
```

## Demo Data

The `seed_demo` command recreates the storefront demo data:

- 44 realistic product entries.
- Popular real-brand style product names.
- Product categories and subcategories.
- Hero sliders.
- Promo banners.
- Blog posts.
- Static pages.
- Demo admin user.

Run:

```bash
python manage.py seed_demo
```

Demo admin credentials created only if no `admin` user exists:

```text
Username: admin
Password: admin12345
```

## Admin Access

```text
http://127.0.0.1:8000/admin/
```

Admin features:

- Manage products, categories, variants, reviews, and stock alerts.
- Manage orders, carts, coupons, addresses, and payments.
- Manage blogs, pages, homepage sections, hero slides, and banners.
- View analytics dashboard.
- Update SEO metadata.

## SEO Features

This Django ecommerce website includes:

- SEO-friendly server-rendered product pages.
- Product meta title and meta description.
- Category meta title and meta description.
- Blog SEO content.
- Static CMS pages for trust and organic ranking.
- Dynamic `robots.txt`.
- Dynamic `sitemap.xml`.
- Canonical URLs.
- Open Graph site metadata.
- Clean product/category URLs.
- Lazy-loaded images.
- Fast server-rendered HTML for crawlers.

Important SEO routes:

```text
/robots.txt
/sitemap.xml
/shop/
/category/<slug>/
/product/<slug>/
/blogs/
/pages/<slug>/
```

## AJAX and SPA-Like UX

The project keeps Django templates but improves speed with AJAX and partial updates.

JavaScript modules:

- [static/js/api.js](static/js/api.js): CSRF-safe Fetch API wrapper.
- [static/js/ui.js](static/js/ui.js): DOM updates, toast notifications, loading states, cart/wishlist/shop AJAX.
- [static/js/main.js](static/js/main.js): Navigation, minicart, search overlay, product details, UI interactions.

AJAX features:

- Add to cart without full reload.
- Remove cart item without full reload.
- Update cart quantity without full reload.
- Update cart totals dynamically.
- Update mini cart drawer dynamically.
- Wishlist toggle without full reload.
- Product filtering with Fetch API.
- Product load-more button.
- History API support for filter URLs.
- Toast notification system.
- Loading spinner and disabled button states.

## Deployment

The project includes `render.yaml` for Render deployment.

Production stack:

- Render web service.
- Render PostgreSQL.
- Gunicorn WSGI server.
- WhiteNoise static file serving.
- Secure cookies and HTTPS redirect when `DEBUG=False`.

Render build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Render start command:

```bash
python manage.py migrate --noinput && gunicorn zynvo_project.wsgi --log-file -
```

## Testing

Run all tests:

```bash
python manage.py test
```

Run app-specific tests:

```bash
python manage.py test accounts
python manage.py test catalog
python manage.py test orders
python manage.py test profiles
```

Run system check:

```bash
python manage.py check
```

## Useful Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Seed demo data
python manage.py seed_demo

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver

# Run tests
python manage.py test
```

## Feature Tags

`Django` `Django 6` `Python` `Ecommerce` `Online Store` `Shopping Cart` `Checkout` `Payment Flow` `Order Tracking` `Wishlist` `User Authentication` `User Profile` `Django Admin` `Jazzmin` `Tailwind CSS` `Bootstrap 5` `AJAX` `Fetch API` `SPA-like UX` `SEO` `Sitemap` `Robots.txt` `Blog CMS` `Product Variants` `Coupons` `Rewards` `Render Deployment` `Gunicorn` `WhiteNoise` `PostgreSQL` `SQLite`

## License

This project is available for learning, portfolio, and ecommerce starter use. Review dependencies and third-party image/source policies before commercial deployment.
