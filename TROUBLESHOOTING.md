# 🔧 Troubleshooting & FAQ

## مشکلات رایج و راه‌حل‌های آنها

---

## 🔴 Backend Issues

### 1. خطای Import Module

**مشکل:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**حل:**
```bash
# مطمئن شوید virtual environment فعال است
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows

# سپس دوباره requirements را نصب کنید
pip install -r requirements.txt
```

---

### 2. خطای DATABASE

**مشکل:**
```
sqlite3.OperationalError: unable to open database file
```

**حل:**
```bash
# مطمئن شوید در دایرکتوری backend هستید
cd backend

# دیتابیس را دوباره بسازید
python -c "from database import Base, engine; from models import *; Base.metadata.create_all(bind=engine)"
```

---

### 3. Port 8000 در استفاده است

**مشکل:**
```
Address already in use
```

**حل:**
```bash
# یک port دیگر استفاده کنید
uvicorn main:app --port 8001

# یا پروسه قدیمی را بسته‌اید (Linux/Mac)
lsof -i :8000
kill -9 <PID>
```

---

### 4. CORS Error

**مشکل:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**حل:**
در `.env` فایل تنظیم کنید:
```
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

### 5. خطای JWT/Token

**مشکل:**
```
Could not validate credentials
```

**حل:**
```bash
# SECRET_KEY را بررسی کنید
# باید در .env تنظیم شده باشد
SECRET_KEY=your-very-secret-key-minimum-32-characters
```

---

## 🔴 Frontend Issues

### 1. API متصل نیست

**مشکل:**
```
Failed to fetch
API Error
```

**حل:**
1. مطمئن شوید Backend اجرا می‌شود: `http://localhost:8000`
2. CORS تنظیم‌شده است (.env)
3. درصفحه کنسول (F12) خطا را بررسی کنید

---

### 2. صفحه سفید است

**مشکل:**
صفحه خالی نمایش داده می‌شود

**حل:**
```bash
# فایل‌های را بررسی کنید
# frontend/ باید شامل این فایل‌ها باشد:
# - index.html
# - static/js/api.js
# - static/js/ui.js
# - static/js/main.js
# - static/css/style.css

# دوباره frontend server را شروع کنید
cd frontend
python -m http.server 3000
```

---

### 3. JavaScript خطا

**مشکل:**
```
Uncaught ReferenceError
```

**حل:**
1. مطمئن شوید تمام JS فایل‌ها در صحیح هستند
2. کنسول (F12) را بررسی کنید
3. Cache مرورگر را پاک کنید (Ctrl+Shift+Delete)

---

## 🔴 Database Issues

### 1. بکاپ گیری

```bash
# SQLite
cp ikco_store.db ikco_store.db.backup

# PostgreSQL
pg_dump -U user ikco_store > backup.sql
```

### 2. تغییر Database

برای تغییر از SQLite به PostgreSQL:

```env
# قبل (SQLite):
DATABASE_URL=sqlite:///./ikco_store.db

# بعد (PostgreSQL):
DATABASE_URL=postgresql://user:password@localhost/ikco_store
```

سپس دیتابیس را دوباره بسازید:
```bash
python -c "from database import Base, engine; from models import *; Base.metadata.create_all(bind=engine)"
```

---

## 🔴 Email Issues

### 1. ایمیل ارسال نمی‌شود

**حل برای Gmail:**
1. 2FA را فعال کنید
2. App Password بسازید: https://myaccount.google.com/apppasswords
3. `.env` را تنظیم کنید:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**برای سرورهای دیگر:**
```env
# Outlook
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587

# Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587

# Custom Server
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
```

---

## 🔴 Performance Issues

### 1. سرور کند است

**حل:**
```bash
# استفاده از Gunicorn (Production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# یا استفاده از Uvicorn با workers
uvicorn main:app --workers 4
```

### 2. Database کند است

```bash
# فهرس‌ها را بررسی کنید
# PostgreSQL
ANALYZE;

# Query optimization
# بررسی کنید کدام queries کند هستند
```

---

## 🔴 Security Issues

### 1. SECRET_KEY ضعیف است

**حل:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

سپس این را در `.env` جایگزین کنید

### 2. HTTPS در Production

```bash
# استفاده از Let's Encrypt
certbot certonly --standalone -d yourdomain.com

# Uvicorn با SSL
uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

---

## ❓ سوالات متداول (FAQ)

### Q: چگونه Admin بسازم؟

```bash
python -c "
from database import SessionLocal
from models.user import User

db = SessionLocal()
admin = User(
    full_name='Admin User',
    email='admin@example.com',
    phone='09121234567',
    hashed_password=User.hash_password('AdminPass123'),
    is_admin=True
)
db.add(admin)
db.commit()
print('Admin created successfully')
"
```

---

### Q: چگونه محصول اضافه کنم؟

**بدون Admin Panel (فعلاً):**

API استفاده کنید:
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "name": "Peykan Plus",
    "slug": "peykan-plus",
    "price": 250000000,
    "category_id": 1,
    "stock": 10
  }'
```

---

### Q: چگونه Stripe فعال کنم؟

1. ثبت‌نام در https://stripe.com
2. API Keys را کپی کنید
3. `.env` را تنظیم کنید:

```env
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

### Q: چگونه TON Payment تست کنم؟

```env
TON_API_URL=https://testnet.toncenter.com/api/v2
```

تست‌نت استفاده کنید (testnet)

---

### Q: چگونه Database را Reset کنم؟

```bash
# SQLite
rm ikco_store.db

# سپس دوباره بسازید:
python -c "from database import Base, engine; from models import *; Base.metadata.create_all(bind=engine)"
```

---

### Q: لاگ‌ها کجا هستند؟

- Backend: `backend/` دایرکتوری
- Frontend: Browser Console (F12)
- Database: `ikco_store.db` یا PostgreSQL logs

---

### Q: چگونه برای Production آماده کنم؟

```bash
# 1. .env تنظیم کنید
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=very-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://...

# 2. Gunicorn استفاده کنید
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# 3. Nginx استفاده کنید (Reverse Proxy)
# Nginx config: https://nginx.org/

# 4. HTTPS فعال کنید
# Let's Encrypt استفاده کنید
```

---

## 📞 کمک بیشتر

اگر مشکل حل نشد:

1. **فایل‌های LOG را بررسی کنید**
2. **Console/Terminal خطا‌ها را ببینید**
3. **Browser DevTools را بازکنید (F12)**
4. **مستندات کامل را بخوانید**

---

✨ **موفق باشید!**
