# 🚀 شروع سریع - IKCO Store

## خلاصه مختصر

این پروژه یک فروشگاه آنلاین حرفه‌ای برای فروش خودروهای ایرانی است که تمام نیازهای یک فروشگاه حرفه‌ای را برطرف می‌کند.

## ✨ مشکلات حل‌شده

### ۱️⃣ مشکلات امنیتی
✅ Secret key از environment variables می‌خوانه (هاردکد نیست)
✅ رمزهای عبور با BCrypt رمزنگاری می‌شوند
✅ JWT tokens برای احراز هویت
✅ CORS مناسب تنظیم شده

### ۲️⃣ پایگاه‌داده واقعی
✅ SQLAlchemy ORM
✅ Support برای SQLite و PostgreSQL
✅ مدل‌های کامل برای تمام entities
✅ Relationships صحیح بین جداول

### ۳️⃣ سیستم محصول کامل
✅ صفحات جزئیات محصول
✅ گالری عکس محصول
✅ مشخصات فنی کامل (موتور، گیربکس، سوخت، رنگ)
✅ سیستم فیلترینگ پیشرفته
✅ جستجوی قدرتمند

### ۴️⃣ سیستم سفارش‌ها
✅ ایجاد سفارش کامل
✅ پیگیری سفارش بی‌درنگ
✅ مدیریت وضعیت سفارش (7 وضعیت مختلف)
✅ ارسال ایمیل خودکار
✅ لغو و بازگشت سفارش

### ۵️⃣ سیستم پرداخت حرفه‌ای
✅ پرداخت با کارت بانکی (Stripe)
✅ پرداخت اقساطی تا 60 ماه
✅ پرداخت با TON
✅ محاسبه خودکار سود اقساط

### ۶️⃣ پنل کاربری
✅ ثبت‌نام/ورود امن
✅ مدیریت پروفایل
✅ سابقه سفارش‌ها
✅ لیست علاقه‌مندی‌ها
✅ نظرات و رتبه‌بندی

### ۷️⃣ صفحات ضروری
✅ صفحه اصلی
✅ صفحه محصولات (با فیلتر و جستجو)
✅ صفحه درباره ما
✅ صفحه تماس با ما
✅ صفحه پیگیری سفارش
✅ صفحه شرایط فروش و ضمانت
✅ داشبوردهای مختلف

### ۸️⃣ SEO و Performance
✅ Meta tags صحیح
✅ Open Graph support
✅ Schema.org structured data
✅ Responsive design
✅ RTL support کامل

## 📦 نصب سریع (۵ دقیقه)

### مرحله 1: Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # یا venv\Scripts\activate در Windows
pip install -r requirements.txt
cp .env.example .env
python main.py
```

سرور شروع می‌شود: http://localhost:8000

### مرحله 2: Frontend
```bash
cd frontend
python -m http.server 3000
```

برروید: http://localhost:3000

## 🎯 فایل‌های اصلی

### Backend
- `main.py` - نقطه ورود برنامه
- `config.py` - تنظیمات (از env میخونه)
- `database.py` - نظام دیتابیس
- `models/` - مدل‌های دیتابیس
- `schemas/` - Pydantic validation schemas
- `routes/` - API endpoints
- `utils/` - Helper functions (auth، email، payment)

### Frontend
- `index.html` - صفحه اصلی (RTL)
- `static/css/style.css` - تمام CSS
- `static/js/api.js` - API calls
- `static/js/ui.js` - UI helpers
- `static/js/main.js` - Logik اصلی

## 🔌 API Endpoints (خلاصه)

```
👤 Authentication
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout

🛍️ Products
GET    /api/v1/products
GET    /api/v1/products/{id}
GET    /api/v1/products/featured/list

📦 Orders
POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{id}
PATCH  /api/v1/orders/{id}/status

❤️ Wishlist
GET    /api/v1/wishlist
POST   /api/v1/wishlist
DELETE /api/v1/wishlist/{id}

⭐ Reviews
GET    /api/v1/reviews/product/{id}
POST   /api/v1/reviews

👤 Users
GET    /api/v1/users/me
PATCH  /api/v1/users/me
```

## 📊 جدول‌های دیتابیس

```
users (کاربران)
├─ id, email, phone, full_name, hashed_password
├─ address, city, postal_code
└─ created_at, last_login

products (محصولات)
├─ id, name, slug, description
├─ price, discount_percentage, discount_price
├─ category_id
├─ engine_cc, transmission, fuel_type, seats, color
├─ stock, is_active, is_featured, is_presale
├─ average_rating, review_count
└─ created_at, updated_at

orders (سفارش‌ها)
├─ id, order_number, user_id
├─ total_amount, discount_amount, final_amount
├─ shipping_address, shipping_city, shipping_postal_code
├─ payment_method, payment_status
├─ status (pending/confirmed/processing/shipped/delivered/cancelled)
└─ created_at, shipped_at, delivered_at

products_images (عکس‌های محصول)
├─ id, product_id, image_url
└─ is_primary, display_order

reviews (نظرات)
├─ id, product_id, user_id
├─ rating (1-5), title, comment
├─ is_verified_purchase, helpful_count
└─ created_at

wishlists (لیست علاقه‌مندی‌ها)
├─ id, user_id, product_id
└─ created_at
```

## 🎨 طراحی
- **RTL Support**: تمام صفحات فارسی‌است
- **Dark Theme**: رنگ‌های تیره و حرفه‌ای
- **Responsive**: قابل نمایش در موبایل، تبلت، کامپیوتر
- **Modern UI**: Gradient، shadows، transitions

## 🔐 امنیت

✅ Password hashing: BCrypt
✅ API Auth: JWT tokens
✅ CORS: تنظیم‌شده برای origins مجاز
✅ Env variables: بدون کد‌های حساس
✅ Validation: Pydantic schemas

## 🚀 Production Ready

### نصب برای Production
```bash
# استفاده از Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# یا Docker
docker-compose up
```

### نکات مهم
1. DEBUG را False کنید
2. SECRET_KEY را تغییر دهید
3. ALLOWED_ORIGINS را تنظیم کنید
4. Database را PostgreSQL تغییر دهید
5. SMTP را برای ایمیل‌ها تنظیم کنید

## 📝 نمونه‌ عملیات

### ثبت‌نام و ورود
```javascript
// ثبت‌نام
await registerUser({
  full_name: "علی احمدی",
  email: "ali@example.com",
  phone: "09121234567",
  password: "SecurePass123!"
});

// ورود
await loginUser("ali@example.com", "SecurePass123!");
```

### خرید محصول
```javascript
// دریافت محصولات
const products = await getProducts({ category_id: 1 });

// ایجاد سفارش
const order = await createOrder({
  shipping_address: "تهران، خیابان فردوسی",
  shipping_city: "تهران",
  shipping_postal_code: "1234567",
  shipping_phone: "09121234567",
  payment_method: "card"
});
```

### اضافه کردن به لیست علاقه‌مندی
```javascript
await addToWishlist(productId);
```

## 🎁 فایل‌های اضافی شامل

- ✅ README.md - مستندات کامل
- ✅ INSTALLATION.md - راهنمای نصب
- ✅ docker-compose.yml - برای deployment سریع
- ✅ Dockerfile - برای containerization
- ✅ .gitignore - برای version control
- ✅ .env.example - نمونه environment variables

## 🆘 سؤالات رایج

**Q: چطور email بفرستم؟**
A: SMTP settings در .env تنظیم کنید

**Q: چطور Stripe فعال کنم؟**
A: STRIPE_API_KEY در .env اضافه کنید

**Q: چطور PostgreSQL استفاده کنم؟**
A: DATABASE_URL را تغییر دهید:
```
DATABASE_URL=postgresql://user:password@localhost/ikco_store
```

**Q: چطور HTTPS فعال کنم؟**
A: Nginx یا Caddy استفاده کنید یا Uvicorn با SSL flags

## 📞 پشتیبانی

- مستندات کامل در README.md
- نصب و راه‌اندازی در INSTALLATION.md
- کد منظم و خودتوضیح

---

**حاضر برای استقرار؟** شروع کنید! 🚀
