#!/bin/bash

# ═══════════════════════════════════════════
# IKCO Store - Setup Script
# فروشگاه ایران خودرو - اسکریپت راه‌اندازی
# ═══════════════════════════════════════════

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       IKCO Store - Setup & Installation                    ║"
echo "║       فروشگاه ایران خودرو - راه‌اندازی                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}🔍 Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo "Install Python 3.8+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# Setup Backend
echo -e "${YELLOW}═════════════════════════════════════════${NC}"
echo -e "${BLUE}📦 Setting up Backend...${NC}"
echo -e "${YELLOW}═════════════════════════════════════════${NC}"
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ backend/ directory not found!${NC}"
    echo "Please make sure you've extracted the files correctly."
    exit 1
fi

cd backend

# Create virtual environment
echo -e "${BLUE}📌 Creating virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✅ Virtual environment created${NC}"
echo ""

# Activate virtual environment
echo -e "${BLUE}📌 Activating virtual environment...${NC}"
source venv/bin/activate || . venv\Scripts\activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install requirements
echo -e "${BLUE}📌 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Setup .env file
echo -e "${BLUE}📌 Setting up .env file...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created from .env.example${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your settings!${NC}"
    echo ""
    echo "Important settings to configure:"
    echo "  - SECRET_KEY (change to a strong random string)"
    echo "  - DATABASE_URL (for PostgreSQL)"
    echo "  - SENDER_EMAIL and SENDER_PASSWORD (for emails)"
    echo "  - STRIPE_API_KEY (if using Stripe)"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi
echo ""

# Database setup
echo -e "${BLUE}📌 Setting up database...${NC}"
python3 << 'PYEOF'
try:
    from database import Base, engine
    from models import *
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Database setup error: {e}")
    print("You can run this manually later")
PYEOF
echo ""

# Go back to root
cd ..

# Setup Frontend
echo -e "${YELLOW}═════════════════════════════════════════${NC}"
echo -e "${BLUE}🎨 Frontend Files Ready${NC}"
echo -e "${YELLOW}═════════════════════════════════════════${NC}"
echo ""

if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ frontend/ directory not found!${NC}"
    echo "Please make sure you've extracted the files correctly."
    exit 1
fi

echo -e "${GREEN}✅ Frontend files are ready at: ./frontend${NC}"
echo ""

# Final instructions
echo -e "${YELLOW}═════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${YELLOW}═════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1️⃣  Edit backend/.env with your configuration"
echo ""
echo "2️⃣  Start Backend Server:"
echo -e "${GREEN}   cd backend${NC}"
echo -e "${GREEN}   source venv/bin/activate  # Windows: venv\\Scripts\\activate${NC}"
echo -e "${GREEN}   python main.py${NC}"
echo ""
echo "3️⃣  Start Frontend (in another terminal):"
echo -e "${GREEN}   cd frontend${NC}"
echo -e "${GREEN}   python -m http.server 3000${NC}"
echo ""
echo "4️⃣  Open your browser:"
echo -e "${GREEN}   http://localhost:3000${NC}"
echo ""

echo -e "${BLUE}📚 Documentation:${NC}"
echo "  - README.md - Full documentation"
echo "  - QUICK_START.md - Quick start guide"
echo "  - INSTALLATION.md - Detailed installation"
echo ""

echo -e "${GREEN}✨ Your IKCO Store is ready to use!${NC}"
echo ""
