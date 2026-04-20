# Zynvo Ecommerce | Django Ecommerce Website

A modern **Django ecommerce website** for a **single brand online store**, built using **Django**, **SQLite**, **HTML**, **CSS**, **JavaScript**, **Tailwind CSS**, and **Bootstrap**.

This project provides a complete **ecommerce system** with product listings, shopping cart functionality, checkout, payment integration, and an **admin dashboard**. It's an ideal starting point for building an **online store using Django**. 

## Live Demo
[View Live Demo](https://ecommerce-1-pp7c.onrender.com)

## Repository
[GitHub Repository](https://github.com/nur949/ecommerce)

---

## Features

- **Modern ecommerce homepage** with a clean section-based layout
- **Product listing** and **product detail pages** (Django ecommerce UI)
- **Product variations** (size, color, etc.)
- **Shopping cart** and **checkout system**
- **Demo payment integration** (bKash / Stripe-style / COD)
- **Order tracking system**
- **User authentication** (Login / Register system in Django)
- **Blog and CMS pages** for SEO content
- **Customized Django admin dashboard** for easy management
- **Demo data seeder** for quick setup
- **Deployment-ready** Django project (Render + Gunicorn + WhiteNoise)

---

## Tech Stack

- **Backend:** Django (Python web framework)
- **Database:** SQLite (Local), PostgreSQL (Production)
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Tailwind CSS, Bootstrap
- **Deployment:** Render, Gunicorn, WhiteNoise

---

## Installation Guide (Run Django Ecommerce Locally)

Follow the steps below to run this **Django ecommerce project locally**.

```bash
# 1. Clone the repository
git clone https://github.com/nur949/ecommerce.git
cd ecommerce

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Apply migrations
python manage.py migrate

# 6. Seed demo data
python manage.py seed_demo

# 7. Run Django server
python manage.py runserver

Open in browser:
http://127.0.0.1:8000/ 
