from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ========== USER SCHEMAS ==========

class UserBase(BaseModel):
    email: EmailStr
    phone: str
    name: str

class UserRegister(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_admin: bool
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    national_id: Optional[str]
    city: Optional[str]
    address: Optional[str]
    last_login: Optional[datetime]

# ========== AUTHENTICATION ==========

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# ========== CATEGORY SCHEMAS ==========

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

# ========== PRODUCT SCHEMAS ==========

class SpecificationItem(BaseModel):
    label: str
    value: str

class ProductBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    slug: str
    description: Optional[str] = None
    specifications: Optional[List[SpecificationItem]] = None
    category_id: int

class ProductCreate(ProductBase):
    base_price: int  # تومان
    sale_price: Optional[int] = None
    discount_percentage: Optional[float] = 0
    stock: int = 0
    sku: Optional[str] = None
    main_image: Optional[str] = None
    images: Optional[List[str]] = None
    is_featured: bool = False
    is_presale: bool = False
    presale_deadline: Optional[datetime] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[int] = None
    sale_price: Optional[int] = None
    discount_percentage: Optional[float] = None
    stock: Optional[int] = None
    is_featured: Optional[bool] = None
    is_presale: Optional[bool] = None
    is_active: Optional[bool] = None

class ProductListResponse(BaseModel):
    id: int
    name: str
    slug: str
    base_price: int
    sale_price: Optional[int]
    discount_percentage: float
    stock: int
    main_image: Optional[str]
    is_featured: bool
    is_presale: bool
    category: CategoryResponse
    
    class Config:
        from_attributes = True

class ProductDetailResponse(ProductListResponse):
    name_en: Optional[str]
    description: Optional[str]
    specifications: Optional[List[SpecificationItem]]
    images: Optional[List[str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    reviews_count: Optional[int] = 0
    average_rating: Optional[float] = 0

class PaginatedProductResponse(BaseModel):
    items: List[ProductListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# ========== REVIEW SCHEMAS ==========

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    title: Optional[str]
    content: Optional[str]
    verified_purchase: bool
    helpful_count: int
    unhelpful_count: int
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True

# ========== CART SCHEMAS ==========

class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class CartItemResponse(BaseModel):
    product_id: int
    product: ProductListResponse
    quantity: int
    unit_price: int
    total_price: int

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    subtotal: int
    tax: int
    shipping_cost: int
    total: int

# ========== ORDER SCHEMAS ==========

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class OrderCreateRequest(BaseModel):
    shipping_address: str
    shipping_city: str
    shipping_phone: str
    payment_method: str = Field(..., regex="^(bank|ton|installment)$")
    notes: Optional[str] = None
    coupon_code: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    product: ProductListResponse
    quantity: int
    unit_price: int
    total_price: int
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    id: int
    order_number: str
    status: str
    payment_status: str
    total_amount: int
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

class OrderDetailResponse(OrderListResponse):
    user: UserResponse
    shipping_address: str
    shipping_city: str
    shipping_phone: str
    subtotal: int
    tax: int
    shipping_cost: int
    payment_method: Optional[str]
    notes: Optional[str]
    admin_notes: Optional[str]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    updated_at: datetime

class OrderStatusUpdate(BaseModel):
    status: str = Field(..., regex="^(pending|confirmed|processing|shipped|delivered|cancelled)$")
    admin_notes: Optional[str] = None

# ========== PRESALE SCHEMAS ==========

class PresaleRegister(BaseModel):
    product_id: int

class PresaleDetailResponse(BaseModel):
    id: int
    product: ProductDetailResponse
    total_capacity: int
    registered_count: int
    remaining: int
    down_payment: int
    deadline: datetime
    progress_percentage: float

# ========== PAYMENT SCHEMAS ==========

class PaymentInitiate(BaseModel):
    order_id: int
    payment_method: str

class PaymentVerify(BaseModel):
    order_id: int
    transaction_id: str
    payment_method: str

class TONPaymentRequest(BaseModel):
    order_id: int
    amount: int  # تومان
    ton_wallet: str
    callback_url: str

class TONPaymentResponse(BaseModel):
    transaction_id: str
    status: str
    ton_address: str
    amount_ton: float
    deadline: datetime

# ========== WISHLIST SCHEMAS ==========

class WishlistAdd(BaseModel):
    product_id: int

class WishlistResponse(BaseModel):
    id: int
    products: List[ProductListResponse]
    count: int

# ========== SEARCH & FILTER ==========

class SearchQuery(BaseModel):
    q: str
    category_id: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sort: Optional[str] = "newest"  # newest, price_asc, price_desc, rating

class SearchResponse(BaseModel):
    results: List[ProductListResponse]
    total: int
    query: str
    filters: Dict[str, Any]

# ========== PAGE SCHEMAS ==========

class PageResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    seo_title: Optional[str]
    seo_description: Optional[str]
    seo_keywords: Optional[str]
    
    class Config:
        from_attributes = True

# ========== BLOG SCHEMAS ==========

class BlogListResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    featured_image: Optional[str]
    view_count: int
    created_at: datetime
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BlogDetailResponse(BlogListResponse):
    content: str
    seo_title: Optional[str]
    seo_description: Optional[str]

# ========== ADMIN SCHEMAS ==========

class AdminStats(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: int
    total_products: int
    pending_orders: int
    today_orders: int
    today_revenue: int

class AdminDashboard(BaseModel):
    stats: AdminStats
    recent_orders: List[OrderListResponse]
    top_products: List[ProductListResponse]
