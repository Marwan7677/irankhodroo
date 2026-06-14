"""
User Profile Routes - مسیرهای پروفایل کاربر
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserResponse, UserUpdate
from utils.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    دریافت اطلاعات کاربر فعلی
    """
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    به‌روزرسانی اطلاعات کاربر
    """
    if user_data.full_name:
        current_user.full_name = user_data.full_name
    
    if user_data.phone:
        # بررسی تکراری نبودن شماره تلفن
        existing = db.query(User).filter(
            User.phone == user_data.phone,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )
        current_user.phone = user_data.phone
    
    if user_data.address:
        current_user.address = user_data.address
    
    if user_data.city:
        current_user.city = user_data.city
    
    if user_data.postal_code:
        current_user.postal_code = user_data.postal_code
    
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    تغییر رمز عبور کاربر
    """
    if not current_user.verify_password(old_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    current_user.hashed_password = User.hash_password(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.get("/orders/history")
async def get_order_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت سابقه سفارش‌های کاربر
    """
    from models.order import Order
    
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return {
        "total_orders": len(orders),
        "orders": orders
    }

@router.get("/wishlist")
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت لیست علاقه‌مندی‌های کاربر
    """
    from models.wishlist import Wishlist
    from schemas.product import ProductResponse
    
    wishlist_items = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).all()
    
    products = [item.product for item in wishlist_items]
    
    return {
        "total_items": len(products),
        "items": products
    }
