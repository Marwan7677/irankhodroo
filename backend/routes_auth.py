from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import re

from database import get_db
from models import User
from schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    PasswordReset, PasswordResetConfirm
)
from auth import (
    SecurityUtils, authenticate_user, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate Iranian phone number"""
    pattern = r'^(\+98|0)?9\d{9}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False, "رمز عبور باید حداقل ۸ کاراکتر باشد"
    
    if not re.search(r'[A-Z]', password):
        return False, "رمز عبور باید حداقل یک حرف بزرگ داشته باشد"
    
    if not re.search(r'[a-z]', password):
        return False, "رمز عبور باید حداقل یک حرف کوچک داشته باشد"
    
    if not re.search(r'\d', password):
        return False, "رمز عبور باید حداقل یک رقم داشته باشد"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "رمز عبور باید حداقل یک کاراکتر ویژه داشته باشد"
    
    return True, "OK"


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    ثبت‌نام کاربر جدید
    """
    # Validate input
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ایمیل نامعتبر است"
        )
    
    if not validate_phone(user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="شماره موبایل نامعتبر است"
        )
    
    is_strong, message = validate_password_strength(user_data.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check if user already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این ایمیل قبلاً ثبت شده است"
        )
    
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این شماره موبایل قبلاً ثبت شده است"
        )
    
    # Create new user
    hashed_password = SecurityUtils.get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        phone=user_data.phone,
        name=user_data.name,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": new_user.id},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    ورود کاربر با ایمیل و رمز عبور
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا رمز عبور نادرست است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = __import__('datetime').datetime.utcnow()
    db.commit()
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login-phone", response_model=TokenResponse)
async def login_with_phone(
    phone: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    ورود کاربر با شماره موبایل و رمز عبور
    """
    user = db.query(User).filter(User.phone == phone).first()
    
    if not user or not SecurityUtils.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شماره موبایل یا رمز عبور نادرست است"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    تازه کردن توکن دسترسی
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": current_user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    دریافت اطلاعات کاربر جاری
    """
    return current_user


@router.post("/password-reset")
async def request_password_reset(
    request: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    درخواست تغییر رمز عبور (ارسال ایمیل)
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "اگر این ایمیل در سیستم وجود داشته باشد، لینک بازیابی ارسال خواهد شد"}
    
    # In production, send email with reset token
    # For now, just return success message
    # TODO: Implement email sending with reset token
    
    return {"message": "لینک بازیابی رمز عبور به ایمیل شما ارسال شد"}


@router.post("/password-reset-confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    تأیید و تغییر رمز عبور
    """
    # TODO: Verify token and change password
    try:
        payload = __import__('jose').jwt.decode(
            request.token,
            "SECRET_KEY",  # Use actual secret
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="توکن نامعتبر یا منقضی است"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    
    user.hashed_password = SecurityUtils.get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "رمز عبور با موفقیت تغییر کرد"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    خروج از حساب
    (در عملیات توکن محور، صرفاً توکن را از کلاینت حذف می‌کنیم)
    """
    return {"message": "با موفقیت خارج شدید"}
