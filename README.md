# IKCO Store - فروشگاه آنلاین ایران خودرو

یک فروشگاه آنلاین حرفه‌ای برای فروش خودروهای ایرانی با تمامی ویژگی‌های مورد نیاز.

## ✨ ویژگی‌های اصلی

### 🛍️ سیستم فروشگاهی
- **مدیریت محصولات**: کاتالوگ جامع خودروها
- **سیستم دسته‌بندی**: سازمان بندی محصولات
- **فیلترینگ و جستجو**: جستجو پیشرفته و فیلتر‌های قیمت، نوع سوخت، گیربکس
- **سبد خرید**: سیستم سبد خرید کامل
- **مقایسه محصولات**: مقایسه مشخصات خودروها

### 💳 سیستم پرداخت
- **درگاه بانکی**: پرداخت با کارت اعتباری (Stripe)
- **پرداخت اقساطی**: فروش اقساطی تا 60 ماه
- **پرداخت با تون**: پرداخت با رمزارز TON
- **محاسبه خودکار**: محاسبه خودکار سود اقساط

### 👤 مدیریت کاربران
- **ثبت‌نام/ورود**: سیستم احراز هویت امن
- **پروفایل کاربر**: مدیریت اطلاعات شخصی
- **سابقه سفارش‌ها**: رگ‌بار تمام سفارش‌ها
- **لیست علاقه‌مندی‌ها**: ذخیره محصولات علاقه‌مندی

### 📦 مدیریت سفارش‌ها
- **ایجاد سفارش**: سفارش‌گذاری ساده
- **پیگیری سفارش**: پیگیری بی‌درنگ وضعیت سفارش
- **مدیریت وضعیت**: تغییر وضعیت سفارش توسط مدیران
- **ارسال ایمیل**: ایمیل تأیید سفارش و اطلاعات ارسال

### ⭐ نظرات و رتبه‌بندی
- **سیستم نظرات**: ثبت نظرات مشتریان
- **رتبه‌بندی محصولات**: رتبه‌بندی تا 5 ستاره
- **تأیید خرید**: نشان‌دهی محصولات خریده‌شده
- **مفید شمردن**: مارک کردن نظرات مفید

### 🔐 امنیت
- **JWT Authentication**: احراز هویت امن
- **تشفیر رمز عبور**: BCrypt hashing
- **متغیرهای محیطی**: بدون کد‌های حساس در کد
- **CORS Configuration**: کنترل دسترسی متقاطع

### 📱 طراحی‌ریسپانسیو
- **RTL Support**: دعم کامل راست‌به‌چپ
- **موبایل‌ فرندلی**: طراحی مناسب برای تمام دستگاه‌ها
- **Dark Mode Ready**: آماده‌سازی برای حالت شب
- **رابط کاربری حرفه‌ای**: طراحی مدرن و زیبا

## 🚀 شروع به کار

### پیش‌نیازها
- Python 3.8+
- Node.js (اختیاری)
- PostgreSQL یا SQLite

### نصب Backend

```bash
# رفتن به دایرکتوری backend
cd backend

# نصب dependencies
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
cp .env.example .env
# سپس .env را ویرایش کنید

# ایجاد دیتابیس
python -m alembic upgrade head

# اجرای سرور
python main.py
```

### نصب Frontend

```bash
# دایرکتوری frontend از طریق HTTP سرو کنید
# یا از یک فایل سرور Python استفاده کنید:
cd frontend
python -m http.server 3000
```

سپس در مرورگر به `http://localhost:3000` بروید.

## 📁 ساختار پروژه

```
ikco-store-complete/
├── backend/
│   ├── models/          # مدل‌های SQLAlchemy
│   ├── schemas/         # Pydantic schemas
│   ├── routes/          # API routes
│   ├── utils/           # Helper functions
│   ├── config.py        # تنظیمات
│   ├── database.py      # نظام پایگاه‌داده
│   ├── main.py          # نقطه ورود برنامه
│   └── requirements.txt  # وابستگی‌ها
├── frontend/
│   └── index.html       # صفحه اصلی
└── static/
    ├── js/              # فایل‌های JavaScript
    └── css/             # فایل‌های CSS
```

## 🔌 API Endpoints

### احراز هویت
- `POST /api/v1/auth/register` - ثبت‌نام
- `POST /api/v1/auth/login` - ورود
- `POST /api/v1/auth/logout` - خروج
- `POST /api/v1/auth/refresh-token` - تازه‌سازی توکن

### محصولات
- `GET /api/v1/products` - دریافت لیست محصولات
- `GET /api/v1/products/{id}` - جزئیات محصول
- `POST /api/v1/products` - ایجاد محصول (مدیران)
- `GET /api/v1/products/featured/list` - محصولات ویژه

### سفارش‌ها
- `POST /api/v1/orders` - ایجاد سفارش
- `GET /api/v1/orders` - سفارش‌های کاربر
- `GET /api/v1/orders/{id}` - جزئیات سفارش
- `PATCH /api/v1/orders/{id}/status` - تغییر وضعیت (مدیران)

### کاربران
- `GET /api/v1/users/me` - اطلاعات کاربر فعلی
- `PATCH /api/v1/users/me` - بروزرسانی پروفایل
- `POST /api/v1/users/change-password` - تغییر رمز عبور

### نظرات
- `GET /api/v1/reviews/product/{id}` - نظرات محصول
- `POST /api/v1/reviews` - اضافه کردن نظر
- `PATCH /api/v1/reviews/{id}` - بروزرسانی نظر
- `DELETE /api/v1/reviews/{id}` - حذف نظر

### لیست علاقه‌مندی‌ها
- `GET /api/v1/wishlist` - دریافت لیست
- `POST /api/v1/wishlist` - اضافه کردن
- `DELETE /api/v1/wishlist/{id}` - حذف

## 📊 پایگاه‌داده

### جداول اصلی:
- **users**: کاربران
- **products**: محصولات
- **categories**: دسته‌بندی‌ها
- **orders**: سفارش‌ها
- **order_items**: آیتم‌های سفارش
- **reviews**: نظرات
- **wishlists**: لیست‌های علاقه‌مندی

## 🔧 متغیرهای محیطی

```env
# Database
DATABASE_URL=sqlite:///./ikco_store.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# Email
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Stripe
STRIPE_API_KEY=sk_test_...

# TON Blockchain
TON_API_URL=https://testnet.toncenter.com/api/v2
```

## 🎨 انتخاب‌های طراحی

### رنگ‌ها
- **Primary**: #1a73e8 (آبی)
- **Secondary**: #34a853 (سبز)
- **Danger**: #ea4335 (قرمز)
- **Dark BG**: #1a1a1a
- **Light BG**: #f5f5f5

### فونت‌ها
- **Font Family**: Vazirmatn (فارسی)
- **Fallback**: Arial, sans-serif

## 📄 لایسنس

این پروژه تحت لایسنس MIT است.

## 👥 مشارکت

برای مشارکت در پروژه:
1. Fork کنید
2. یک branch جدید بسازید
3. تغییرات خود را commit کنید
4. یک Pull Request بسازید

## 📞 تماس

- ایمیل: info@ikcostore.com
- تلفن: 021-1234567

---

**نسخه**: 1.0.0
**آخرین به‌روزرسانی**: 2024
