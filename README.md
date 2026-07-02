# BSSREUNION — Baraibunia Secondary School Reunion Registration Portal

Django (MVT) দিয়ে বানানো full registration + payment + e-ticket system। নিচে স্টেপ বাই স্টেপ
সেটআপ গাইড দেওয়া হলো।

## Features

- Public registration form (নাম, ফোন, ইমেইল, পাসিং ইয়ার, ডিপার্টমেন্ট/ক্লাস, রক্তের গ্রুপ, টি-শার্ট সাইজ)
- শুধুমাত্র **Baraibunia Secondary School** এর ছাত্র-ছাত্রীদের জন্য রেজিস্ট্রেশন (স্কুলের নাম/থিম `settings.py` থেকে পরিবর্তনযোগ্য)
- SSLCommerz Payment Gateway ইন্টিগ্রেশন (sandbox + live দুটোই সাপোর্ট করে)
- পেমেন্ট সফল হলে **automatically**:
  - QR কোডসহ PDF Entry Ticket জেনারেট হয়
  - Entry Ticket ইমেইলে পাঠানো হয় (PDF attachment সহ)
  - আলাদাভাবে SSLCommerz Payment Receipt ইমেইলও পাঠানো হয়
- QR কোড স্ক্যান করলে ticket verify হওয়ার পেজ ওপেন হয় (gate এ যাচাইয়ের জন্য)
- কাস্টম Admin Panel (`/admin-panel/`):
  - সব রেজিস্ট্রেশনের লিস্ট, পেমেন্ট স্ট্যাটাস, চেক-ইন স্ট্যাটাস
  - নাম / ফোন / Registration ID দিয়ে সার্চ
  - প্রতিটি রেজিস্ট্রেশনের ডিটেইল পেজ + check-in toggle
- Django built-in admin (`/django-admin/`) ও আছে, পুরো ডাটা ম্যানেজ করার জন্য
- Bengali + English mixed UI, ক্লিন নেভি-গোল্ড থিম, mobile responsive

## Project Structure

```
bssreunion/
├── bssreunion/              # project settings, urls
├── registration/            # main app
│   ├── models.py            # Registrant model
│   ├── forms.py
│   ├── views.py              # registration, payment callbacks, admin panel
│   ├── sslcommerz.py        # SSLCommerz API integration
│   ├── ticket_utils.py      # QR + PDF ticket generator
│   ├── email_utils.py       # ticket + receipt email sender
│   ├── fonts/                # Bengali font for PDF generation
│   └── migrations/
├── templates/registration/  # all HTML templates
├── static/css/main.css      # design system
├── requirements.txt
├── .env.example
└── manage.py
```

## 1. Setup (Local Development)

```bash
# Virtual environment বানান
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Dependencies install করুন
pip install -r requirements.txt

# .env ফাইল বানান
cp .env.example .env
# এখন .env ফাইল খুলে আপনার SSLCommerz store_id/password, email credentials দিন

# Migration চালান
python manage.py makemigrations
python manage.py migrate

# Admin user বানান (এটা দিয়েই /admin-panel/ এ লগইন করবেন)
python manage.py createsuperuser

# সার্ভার চালু করুন
python manage.py runserver
```

ব্রাউজারে দেখুন:
- Public site → http://127.0.0.1:8000/
- Registration form → http://127.0.0.1:8000/register/
- Admin panel → http://127.0.0.1:8000/admin-panel/login/
- Django admin → http://127.0.0.1:8000/django-admin/

> Local এ `.env` লোড করতে চাইলে `python-dotenv` ব্যবহার করতে পারেন, অথবা সরাসরি export করতে
> পারেন: `export $(cat .env | grep -v '^#' | xargs)`

## 2. SSLCommerz Setup

1. https://developer.sslcommerz.com/registration/ এ গিয়ে sandbox account খুলুন (ফ্রি)।
2. Sandbox Store ID ও Store Password পাবেন email এ।
3. `.env` এ বসিয়ে দিন:
   ```
   SSLCOMMERZ_STORE_ID=your_sandbox_store_id
   SSLCOMMERZ_STORE_PASSWORD=your_sandbox_store_password
   SSLCOMMERZ_IS_SANDBOX=True
   ```
4. লাইভে যাওয়ার সময় SSLCommerz থেকে live store credentials নিয়ে `SSLCOMMERZ_IS_SANDBOX=False` করে দিন।
5. **Important:** `SITE_BASE_URL` অবশ্যই আপনার পাবলিক ডোমেইন/সাব-ডোমেইন হতে হবে (e.g.
   `https://bssreunion.com`), কারণ SSLCommerz এই URL ব্যবহার করে success/fail/cancel/IPN
   callback পাঠায়। Local এ test করলে [ngrok](https://ngrok.com) দিয়ে public URL বানিয়ে
   ব্যবহার করুন, কারণ SSLCommerz sandbox `127.0.0.1` এ callback দিতে পারবে না।

## 3. Email (SMTP) Setup

Gmail ব্যবহার করতে চাইলে:
1. Gmail এ 2-Step Verification অন করুন।
2. https://myaccount.google.com/apppasswords থেকে একটা **App Password** জেনারেট করুন।
3. `.env` এ বসান:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=youremail@gmail.com
   EMAIL_HOST_PASSWORD=generated_app_password
   ```

Development এ টেস্ট করার সময় `EMAIL_BACKEND` কে console backend রাখলেই হবে — ইমেইলের
content টার্মিনালে প্রিন্ট হয়ে যাবে, আসলে কোনো ইমেইল যাবে না।

## 4. School / Event নাম পরিবর্তন

`bssreunion/settings.py` ফাইলের নিচের অংশ থেকে অথবা `.env` থেকে পরিবর্তন করুন:

```python
SCHOOL_NAME = "Baraibunia Secondary School"
EVENT_SHORT_NAME = "BSSREUNION"
EVENT_FULL_NAME = "BSS Reunion 2026"
EVENT_DATE_TEXT = "July 10, 2026"
EVENT_VENUE = "Baraibunia Secondary School Campus"
REGISTRATION_FEE = 500
```

## 5. Production Deployment (সংক্ষেপে)

```bash
# .env এ production values দিন:
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com
SITE_BASE_URL=https://yourdomain.com
SSLCOMMERZ_IS_SANDBOX=False

# Static files collect করুন
python manage.py collectstatic

# Gunicorn দিয়ে রান করুন (Nginx এর পেছনে)
gunicorn bssreunion.wsgi:application --bind 0.0.0.0:8000

# PostgreSQL ব্যবহার করতে চাইলে .env এ:
DB_ENGINE=postgres
DB_NAME=bssreunion
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
```

Nginx + Gunicorn + PM2/systemd + Let's Encrypt SSL দিয়ে স্ট্যান্ডার্ড Django deployment হিসেবে
সার্ভারে বসিয়ে দিলেই চলবে (আগের মতো Hetzner/VPS সার্ভারেই deploy করা যাবে)।

## 6. Admin Panel ব্যবহার

- লগইন: `/admin-panel/login/` (createsuperuser দিয়ে বানানো username/password দিয়ে)
- Dashboard এ মোট রেজিস্ট্রেশন, Paid সংখ্যা, Checked-in সংখ্যা, এবং Total Revenue দেখা যাবে
- উপরের সার্চ বক্স দিয়ে নাম/ফোন/Registration ID দিয়ে খোঁজা যাবে, এবং স্ট্যাটাস অনুযায়ী ফিল্টার করা যাবে
- প্রতিটি registrant এর "View" এ ক্লিক করলে ডিটেইল পেজ এ গিয়ে check-in mark করা যাবে এবং
  PDF ticket ডাউনলোড করা যাবে

## 7. Gate Entry Verification Flow

1. টিকেটের QR কোডে একটা ইউনিক verify link থাকে: `/verify/<registration_id>/<token>/`
2. গেটে স্ক্যান করলেই registrant এর নাম, পেমেন্ট স্ট্যাটাস, এবং check-in স্ট্যাটাস দেখাবে
3. স্টাফ admin-panel এ লগইন করা থাকলে "Mark as Checked-in" বাটনে ক্লিক করে এন্ট্রি কনফার্ম করতে পারবে
4. শুধুমাত্র `payment_status = paid` হলেই check-in বাটন দেখাবে

## Notes

- কোনো QR code library বা PDF library অতিরিক্ত API key লাগে না — সব local এ generate হয়।
- Bengali টেক্সট সঠিকভাবে PDF এ দেখানোর জন্য `registration/fonts/` এ Noto Sans Bengali font
  bundled আছে — এটা ডিলিট করবেন না।
- প্রতিটি Registrant এর জন্য unique `transaction_id`, `registration_id`, এবং `verify_token`
  (UUID) অটো জেনারেট হয়, তাই duplicate/forged টিকেট তৈরি করা প্রায় অসম্ভব।
# bssreunion
