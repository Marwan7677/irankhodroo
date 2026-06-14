@echo off
REM ═══════════════════════════════════════════
REM IKCO Store - Setup Script (Windows)
REM فروشگاه ایران خودرو - اسکریپت راه‌اندازی
REM ═══════════════════════════════════════════

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║       IKCO Store - Setup ^& Installation                    ║
echo ║       فروشگاه ایران خودرو - راه‌اندازی                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo 🔍 Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH!
    echo Install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found
echo.

REM Setup Backend
echo ═════════════════════════════════════════
echo 📦 Setting up Backend...
echo ═════════════════════════════════════════
echo.

if not exist "backend" (
    echo ❌ backend\ directory not found!
    echo Please make sure you've extracted the files correctly.
    pause
    exit /b 1
)

cd backend

REM Create virtual environment
echo 📌 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created
echo.

REM Activate virtual environment
echo 📌 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM Install requirements
echo 📌 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Setup .env file
echo 📌 Setting up .env file...
if not exist ".env" (
    copy .env.example .env >nul
    echo ✅ .env file created from .env.example
    echo.
    echo ⚠️  Please edit .env file with your settings!
    echo.
    echo Important settings to configure:
    echo   - SECRET_KEY (change to a strong random string)
    echo   - DATABASE_URL (for PostgreSQL)
    echo   - SENDER_EMAIL and SENDER_PASSWORD (for emails)
    echo   - STRIPE_API_KEY (if using Stripe)
) else (
    echo ✅ .env file already exists
)
echo.

REM Database setup
echo 📌 Setting up database...
python -c "from database import Base, engine; from models import *; Base.metadata.create_all(bind=engine); print('✅ Database tables created successfully')" 2>nul
if errorlevel 1 (
    echo ⚠️  Database setup - you can run this manually later
)
echo.

REM Go back to root
cd ..

REM Setup Frontend
echo ═════════════════════════════════════════
echo 🎨 Frontend Files Ready
echo ═════════════════════════════════════════
echo.

if not exist "frontend" (
    echo ❌ frontend\ directory not found!
    echo Please make sure you've extracted the files correctly.
    pause
    exit /b 1
)

echo ✅ Frontend files are ready at: .\frontend
echo.

REM Final instructions
echo ═════════════════════════════════════════
echo 🎉 Setup Complete!
echo ═════════════════════════════════════════
echo.

echo 📝 Next Steps:
echo.
echo 1️⃣  Edit backend\.env with your configuration
echo.
echo 2️⃣  Start Backend Server:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo 3️⃣  Start Frontend (in another terminal):
echo    cd frontend
echo    python -m http.server 3000
echo.
echo 4️⃣  Open your browser:
echo    http://localhost:3000
echo.

echo 📚 Documentation:
echo   - README.md - Full documentation
echo   - QUICK_START.md - Quick start guide
echo   - INSTALLATION.md - Detailed installation
echo.

echo ✨ Your IKCO Store is ready to use!
echo.

pause
