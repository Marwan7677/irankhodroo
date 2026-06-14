"""
Order Routes - مسیرهای سفارش‌ها
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.order import Order, OrderItem, OrderStatus, PaymentStatus
from models.product import Product
from schemas.order import OrderCreate, OrderResponse, OrderDetail, OrderStatusUpdate
from utils.auth import get_current_user, get_admin_user
from utils.payment import calculate_ton_amount, calculate_installment, verify_ton_payment
from utils.email import send_order_confirmation
from models.user import User
import uuid

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ایجاد سفارش جدید
    """
    # تولید شماره سفارش یکتا
    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # ایجاد سفارش
    new_order = Order(
        user_id=current_user.id,
        order_number=order_number,
        total_amount=0,  # به‌روزرسانی بعدی
        final_amount=0,
        shipping_address=order_data.shipping_address,
        shipping_city=order_data.shipping_city,
        shipping_postal_code=order_data.shipping_postal_code,
        shipping_phone=order_data.shipping_phone,
        payment_method=order_data.payment_method,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING
    )
    
    # اگر اقساط انتخاب شده
    if order_data.payment_method == "installment" and order_data.installment_months:
        new_order.installment_months = order_data.installment_months
        # محاسبه سود اقساط
        installment_info = calculate_installment(
            new_order.total_amount,
            order_data.installment_months
        )
        new_order.installment_rate = installment_info['annual_rate']
    
    # اگر TON انتخاب شده
    if order_data.payment_method == "ton":
        new_order.ton_wallet_address = order_data.ton_wallet_address
    
    db.add(new_order)
    db.flush()
    
    # ارسال ایمیل تأیید
    send_order_confirmation(
        current_user.email,
        order_number,
        new_order.final_amount
    )
    
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("/", response_model=list[OrderResponse])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت سفارش‌های کاربر فعلی
    """
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return orders

@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات سفارش
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.patch("/{order_id}/status", response_model=OrderDetail)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    به‌روزرسانی وضعیت سفارش (فقط مدیران)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = status_update.status
    order.notes = status_update.notes
    
    # به‌روزرسانی تاریخ‌ها
    if status_update.status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.utcnow()
    elif status_update.status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order

@router.post("/{order_id}/verify-ton-payment")
async def verify_ton_payment_endpoint(
    order_id: int,
    transaction_hash: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    تأیید پرداخت TON
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.payment_method != "ton":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order payment method is not TON"
        )
    
    # تأیید تراکنش
    verification = await verify_ton_payment(
        order.ton_wallet_address,
        transaction_hash,
        order.final_amount
    )
    
    if verification["verified"]:
        order.payment_status = PaymentStatus.COMPLETED
        order.ton_transaction_hash = transaction_hash
        order.status = OrderStatus.CONFIRMED
        db.commit()
        
        return {
            "success": True,
            "message": "Payment verified successfully",
            "order": OrderResponse.from_orm(order)
        }
    else:
        return {
            "success": False,
            "message": "Payment verification failed",
            "error": verification.get("error")
        }

@router.get("/tracking/{order_number}")
async def track_order(order_number: str, db: Session = Depends(get_db)):
    """
    پیگیری سفارش با شماره سفارش
    """
    order = db.query(Order).filter(Order.order_number == order_number).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return {
        "order_number": order.order_number,
        "status": order.status,
        "created_at": order.created_at,
        "shipped_at": order.shipped_at,
        "delivered_at": order.delivered_at,
        "total_amount": order.final_amount
    }

@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    لغو سفارش
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order in current status"
        )
    
    order.status = OrderStatus.CANCELLED
    
    if order.payment_status == PaymentStatus.COMPLETED:
        order.payment_status = PaymentStatus.REFUNDED
    
    db.commit()
    
    return {"message": "Order cancelled successfully"}
