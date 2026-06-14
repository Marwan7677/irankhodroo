"""
Review Routes - مسیرهای نظرات و رتبه‌بندی
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.review import Review
from models.product import Product
from models.order import Order, OrderItem
from schemas.review import ReviewCreate, ReviewResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])

@router.get("/product/{product_id}", response_model=list[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    دریافت نظرات محصول
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    
    return reviews

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    اضافه کردن نظر جدید
    """
    # بررسی وجود محصول
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # بررسی اینکه کاربر این محصول را خریده‌ است
    order_item = db.query(OrderItem).join(Order).filter(
        Order.user_id == current_user.id,
        OrderItem.product_id == review_data.product_id
    ).first()
    
    is_verified = bool(order_item)
    
    # بررسی اینکه کاربر قبلاً نظر داده‌ است
    existing_review = db.query(Review).filter(
        Review.product_id == review_data.product_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    # ایجاد نظر جدید
    new_review = Review(
        product_id=review_data.product_id,
        user_id=current_user.id,
        rating=review_data.rating,
        title=review_data.title,
        comment=review_data.comment,
        is_verified_purchase=is_verified
    )
    
    db.add(new_review)
    
    # به‌روزرسانی میانگین رتبه محصول
    avg_rating = db.query(func.avg(Review.rating)).filter(
        Review.product_id == review_data.product_id
    ).scalar() or 0
    
    review_count = db.query(func.count(Review.id)).filter(
        Review.product_id == review_data.product_id
    ).scalar()
    
    product.average_rating = float(avg_rating)
    product.review_count = review_count + 1
    
    db.commit()
    db.refresh(new_review)
    
    return new_review

@router.get("/", response_model=list[ReviewResponse])
async def get_user_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت نظرات کاربر فعلی
    """
    reviews = db.query(Review).filter(
        Review.user_id == current_user.id
    ).order_by(Review.created_at.desc()).all()
    
    return reviews

@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    به‌روزرسانی نظر
    """
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.rating = review_data.rating
    review.title = review_data.title
    review.comment = review_data.comment
    
    db.commit()
    db.refresh(review)
    
    return review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    حذف نظر
    """
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    db.delete(review)
    db.commit()
    
    return None

@router.post("/{review_id}/helpful")
async def mark_helpful(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    علامت‌گذاری نظر به‌عنوان مفید
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.helpful_count += 1
    db.commit()
    
    return {"helpful_count": review.helpful_count}
