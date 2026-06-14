# راهنمای نصب و راه‌اندازی

## نصب Backend

### 1. نصب Python و وابستگی‌ها

```bash
# ایجاد virtual environment
python -m venv venv

# فعال‌سازی virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# نصب وابستگی‌ها
cd backend
pip install -r requirements.txt
```

### 2. تنظیم متغیرهای محیطی

```bash
# کپی کردن فایل .env.example
cp .env.example .env

# ویرایش .env و تنظیم:
SECRET_KEY=your-secret-key-minimum-32-chars
DATABASE_URL=sqlite:///./ikco_store.db
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### 3. ایجاد دیتابیس

```bash
# اگر از Alembic استفاده می‌کنید
alembic upgrade head

# یا به سادگی اجرای برنامه (SQLAlchemy تولید می‌کند)
python main.py
```

### 4. اجرای سرور Backend

```bash
python main.py
```

سرور در `http://localhost:8000` اجرا خواهد شد.

## نصب Frontend

### 1. ساده‌ترین روش (HTTP Server)

```bash
cd frontend
# Python 3
python -m http.server 3000

# Python 2
python -m SimpleHTTPServer 3000
```

سپس به `http://localhost:3000` بروید.

### 2. با Node.js و Live Server

```bash
# نصب live-server
npm install -g live-server

# اجرا
cd frontend
live-server
```

## بررسی سلامت سرور

```bash
curl http://localhost:8000/api/v1/health
```

باید پاسخ زیر را بگیرید:
```json
{
  "status": "healthy",
  "app": "IKCO Store",
  "version": "1.0.0",
  "environment": "development"
}
```

## تنظیم برای Production

### 1. تنظیمات Security

```env
# .env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=use-a-long-random-secret-key
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. استفاده از PostgreSQL

```env
DATABASE_URL=postgresql://user:password@localhost/ikco_store
```

### 3. تنظیم SMTP برای ارسال ایمیل

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### 4. فعال‌سازی HTTPS

```bash
# استفاده از Uvicorn با SSL
python -m uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### 5. استفاده از Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### 6. استفاده از Nginx به‌عنوان Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/frontend/;
    }
}
```

## استفاده از Docker

### Dockerfile برای Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/ikco_store
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ikco_store
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Troubleshooting

### خطای CORS

اگر خطای CORS دریافت می‌کنید:
1. `ALLOWED_ORIGINS` در `.env` را بررسی کنید
2. مرورگر را Refresh کنید
3. کنسول DevTools را بررسی کنید

### خطای Database

```bash
# بررسی دیتابیس
python -c "from database import engine; from models import *; Base.metadata.create_all(bind=engine)"
```

### خطای JWT Token

Token باید در header `Authorization: Bearer <token>` ارسال شود.

### ایمیل ارسال نمی‌شود

1. Gmail برای اپلیکیشن‌های کمتر امن را فعال کنید
2. یا App Password استفاده کنید
3. SMTP تنظیمات را بررسی کنید

## نکات مهم

✅ **قبل از استقرار:**
- [ ] `.env.example` را کپی کرده و `.env` را تنظیم کنید
- [ ] SECRET_KEY را تغییر دهید
- [ ] DATABASE_URL را برای پروداکشن تغییر دهید
- [ ] CORS origins را تنظیم کنید
- [ ] Email credentials را قرار دهید
- [ ] توکن های بانکی/blockchain را اضافه کنید

✅ **تست:**
- [ ] تمام API endpoints را تست کنید
- [ ] ثبت‌نام/ورود را تست کنید
- [ ] سفارش‌گذاری را تست کنید
- [ ] ارسال ایمیل را تست کنید

## منابع مفید

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

سوالات؟ ایمیل: support@ikcostore.com
