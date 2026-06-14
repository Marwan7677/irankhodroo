from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Optional
import json

from database import get_db
from models import Product, Category, Review, User, OrderItem, Order, wishlist
from schemas import (
    ProductListResponse, ProductDetailResponse, ProductCreate, ProductUpdate,
    ReviewCreate, ReviewResponse, CategoryResponse, PaginatedProductResponse,
    SearchQuery, SearchResponse, WishlistAdd, WishlistResponse
)
from auth import get_current_user, get_current_admin

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)

# ===== PRODUCT ENDPOINTS =====

@router.get("", response_model=PaginatedProductResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    category_id: Optional[int] = None,
    is_featured: Optional[bool] = None,
    is_presale: Optional[bool] = None,
    sort: str = "newest",
    db: Session = Depends(get_db)
):
    """
    دریافت لیست محصولات با فیلتر و pagination
    """
    query = db.query(Product).filter(Product.is_active == True)
    
    # Apply filters
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    if is_presale is not None:
        query = query.filter(Product.is_presale == is_presale)
    
    # Apply sorting
    if sort == "newest":
        query = query.order_by(desc(Product.created_at))
    elif sort == "oldest":
        query = query.order_by(asc(Product.created_at))
    elif sort == "price_asc":
        query = query.order_by(asc(Product.sale_price))
    elif sort == "price_desc":
        query = query.order_by(desc(Product.sale_price))
    elif sort == "popular":
        # Join with orders to count purchases
        query = query.outerjoin(OrderItem).group_by(Product.id).order_by(desc(func.count(OrderItem.id)))
    
    # Get total count
    total = query.count()
    
    # Pagination
    skip = (page - 1) * page_size
    products = query.offset(skip).limit(page_size).all()
    
    return PaginatedProductResponse(
        items=[ProductListResponse.from_orm(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/search", response_model=SearchResponse)
async def search_products(
    query: SearchQuery,
    db: Session = Depends(get_db)
):
    """
    جستجو در محصولات
    """
    search_query = db.query(Product).filter(
        Product.is_active == True
    ).filter(
        Product.name.ilike(f"%{query.q}%") |
        Product.description.ilike(f"%{query.q}%") |
        Product.name_en.ilike(f"%{query.q}%")
    )
    
    if query.category_id:
        search_query = search_query.filter(Product.category_id == query.category_id)
    
    if query.min_price:
        search_query = search_query.filter(
            (Product.sale_price >= query.min_price) |
            (Product.base_price >= query.min_price)
        )
    
    if query.max_price:
        search_query = search_query.filter(
            (Product.sale_price <= query.max_price) |
            (Product.base_price <= query.max_price)
        )
    
    # Sorting
    if query.sort == "price_asc":
        search_query = search_query.order_by(asc(Product.sale_price))
    elif query.sort == "price_desc":
        search_query = search_query.order_by(desc(Product.sale_price))
    else:
        search_query = search_query.order_by(desc(Product.created_at))
    
    results = search_query.limit(50).all()
    
    return SearchResponse(
        results=[ProductListResponse.from_orm(p) for p in results],
        total=len(results),
        query=query.q,
        filters={
            "category_id": query.category_id,
            "min_price": query.min_price,
            "max_price": query.max_price
        }
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات یک محصول
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد"
        )
    
    # Get reviews
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    review_count = len(reviews)
    average_rating = sum([r.rating for r in reviews]) / review_count if reviews else 0
    
    response = ProductDetailResponse.from_orm(product)
    response.reviews_count = review_count
    response.average_rating = average_rating
    
    return response


@router.post("", response_model=ProductListResponse, dependencies=[Depends(get_current_admin)])
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    ایجاد محصول جدید (فقط ادمین)
    """
    # Check category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دسته‌بندی یافت نشد"
        )
    
    # Check slug uniqueness
    existing = db.query(Product).filter(Product.slug == product.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این slug قبلاً استفاده شده است"
        )
    
    # Parse specifications if provided
    specs_json = None
    if product.specifications:
        specs_json = json.dumps([s.dict() for s in product.specifications])
    
    new_product = Product(
        name=product.name,
        name_en=product.name_en,
        slug=product.slug,
        description=product.description,
        specifications=specs_json,
        base_price=product.base_price,
        sale_price=product.sale_price or product.base_price,
        discount_percentage=product.discount_percentage,
        stock=product.stock,
        sku=product.sku,
        main_image=product.main_image,
        images=json.dumps(product.images) if product.images else None,
        category_id=product.category_id,
        is_featured=product.is_featured,
        is_presale=product.is_presale,
        presale_deadline=product.presale_deadline
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return ProductListResponse.from_orm(new_product)


@router.put("/{product_id}", response_model=ProductListResponse, dependencies=[Depends(get_current_admin)])
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    به‌روزرسانی محصول (فقط ادمین)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد"
        )
    
    # Update fields
    for field, value in product_update.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return ProductListResponse.from_orm(product)


@router.delete("/{product_id}", dependencies=[Depends(get_current_admin)])
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    حذف محصول (soft delete - تغییر is_active)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد"
        )
    
    product.is_active = False
    db.commit()
    
    return {"message": "محصول با موفقیت حذف شد"}


# ===== CATEGORY ENDPOINTS =====

@router.get("/category/list")
async def list_categories(db: Session = Depends(get_db)):
    """
    دریافت لیست دسته‌بندی‌ها
    """
    categories = db.query(Category).filter(Category.id.in_(
        db.query(Category.id).join(Product).filter(Product.is_active == True)
    )).all()
    
    return [CategoryResponse.from_orm(c) for c in categories]


@router.post("/category", response_model=CategoryResponse, dependencies=[Depends(get_current_admin)])
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    ایجاد دسته‌بندی جدید (فقط ادمین)
    """
    existing = db.query(Category).filter(Category.slug == category.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این slug قبلاً استفاده شده است"
        )
    
    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return CategoryResponse.from_orm(new_category)


# ===== REVIEW ENDPOINTS =====

@router.post("/{product_id}/reviews", response_model=ReviewResponse)
async def create_review(
    product_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ایجاد نظر برای محصول
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد"
        )
    
    # Check if user already reviewed this product
    existing_review = db.query(Review).filter(
        Review.product_id == product_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="شما قبلاً این محصول را نقد کرده‌اید"
        )
    
    # Check if verified purchase
    verified_purchase = db.query(Order).join(OrderItem).filter(
        Order.user_id == current_user.id,
        OrderItem.product_id == product_id,
        Order.payment_status == "paid"
    ).first() is not None
    
    new_review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        verified_purchase=verified_purchase
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return ReviewResponse.from_orm(new_review)


@router.get("/{product_id}/reviews")
async def get_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    دریافت نظرات محصول
    """
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(desc(Review.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    total = db.query(Review).filter(Review.product_id == product_id).count()
    
    return {
        "items": [ReviewResponse.from_orm(r) for r in reviews],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


# ===== WISHLIST ENDPOINTS =====

@router.post("/wishlist/add")
async def add_to_wishlist(
    request: WishlistAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    افزودن محصول به علاقه‌مندی‌ها
    """
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد"
        )
    
    # Check if already in wishlist
    if product not in current_user.wishlist_items:
        current_user.wishlist_items.append(product)
        db.commit()
    
    return {"message": "محصول به علاقه‌مندی‌ها اضافه شد"}


@router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    حذف محصول از علاقه‌مندی‌ها
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد"
        )
    
    if product in current_user.wishlist_items:
        current_user.wishlist_items.remove(product)
        db.commit()
    
    return {"message": "محصول از علاقه‌مندی‌ها حذف شد"}


@router.get("/wishlist")
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    دریافت لیست علاقه‌مندی‌ها
    """
    return WishlistResponse(
        id=current_user.id,
        products=[ProductListResponse.from_orm(p) for p in current_user.wishlist_items],
        count=len(current_user.wishlist_items)
    )
