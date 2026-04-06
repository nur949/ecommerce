# Zynvo Ecommerce

A modern single-brand ecommerce website built with **Django**, **SQLite**, **HTML**, **CSS**, **JavaScript**, **Tailwind CSS**, and **Bootstrap**.

## Live Demo
[View Live Demo](https://ecommerce-1-pp7c.onrender.com)

## Repository
[GitHub Repository](https://github.com/nur949/ecommerce)

---

## Features

- Modern homepage with clean section-based layout
- Product listing and product detail pages
- Product variations support
- Cart and checkout functionality
- Demo payment flow
- Order tracking system
- User authentication (Login / Register)
- Blog and static CMS pages
- Customized Django admin panel
- Demo data seeder
- Deployment-ready configuration with Gunicorn + WhiteNoise

---

## Tech Stack

- **Backend:** Django
- **Database:** SQLite (Local), PostgreSQL (Production)
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Tailwind CSS, Bootstrap
- **Deployment:** Render, Gunicorn, WhiteNoise

---

## Demo Admin Credentials

- **Username:** `admin`
- **Password:** `admin12345`

---

## Installation Guide

Follow the steps below to run the project locally.

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

# 7. Run server
python manage.py runserver
```

Open in browser:
http://127.0.0.1:8000/