"""
Product Routes - مسیرهای محصولات
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database import get_db
from models.product import Product
from models.category import Category
from schemas.product import ProductCreate, ProductResponse, ProductDetail, ProductFilter
from utils.auth import get_current_user, get_admin_user
from models.user import User

router = APIRouter(prefix="/api/v1/products", tags=["Products"])

@router.get("/", response_model=list[ProductResponse])
async def list_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    search: str = Query(None),
    is_presale: bool = Query(None),
    sort_by: str = Query("newest", regex="^(newest|price_asc|price_desc|rating)$")
):
    """
    دریافت لیست محصولات با فیلتر و جستجو
    """
    query = db.query(Product).filter(Product.is_active == True)
    
    # فیلترها
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price:
        query = query.filter(Product.price >= min_price)
    
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    if is_presale is not None:
        query = query.filter(Product.is_presale == is_presale)
    
    # مرتب‌سازی
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "rating":
        query = query.order_by(Product.average_rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    دریافت جزئیات محصول
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.get("/category/{category_id}", response_model=list[ProductResponse])
async def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    دریافت محصولات یک دسته‌بندی
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active == True
    ).offset(skip).limit(limit).all()
    
    return products

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    ایجاد محصول جدید (فقط مدیران)
    """
    # بررسی slug تکراری
    existing = db.query(Product).filter(Product.slug == product_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product slug already exists"
        )
    
    # بررسی دسته‌بندی
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # محاسبه قیمت تخفیف‌خورده
    discount_price = product_data.price * (1 - product_data.discount_percentage / 100)
    
    new_product = Product(
        name=product_data.name,
        slug=product_data.slug,
        description=product_data.description,
        price=product_data.price,
        discount_percentage=product_data.discount_percentage,
        discount_price=discount_price,
        category_id=product_data.category_id,
        engine_cc=product_data.engine_cc,
        transmission=product_data.transmission,
        fuel_type=product_data.fuel_type,
        seats=product_data.seats,
        color=product_data.color,
        stock=product_data.stock,
        is_featured=product_data.is_featured,
        is_presale=product_data.is_presale
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.get("/featured/list")
async def get_featured_products(db: Session = Depends(get_db)):
    """
    دریافت محصولات ویژه
    """
    products = db.query(Product).filter(
        Product.is_featured == True,
        Product.is_active == True
    ).limit(10).all()
    
    return products

@router.get("/presale/list")
async def get_presale_products(db: Session = Depends(get_db)):
    """
    دریافت محصولات پیش‌فروش
    """
    products = db.query(Product).filter(
        Product.is_presale == True,
        Product.is_active == True
    ).all()
    
    return products
