from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, DECIMAL, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# ===== اتصال محصولات و دسته‌بندی‌ها =====
product_category = Table(
    'product_category',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# ===== اتصال علاقه‌مندی‌ها =====
wishlist = Table(
    'wishlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('added_at', DateTime, default=datetime.utcnow)
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # اطلاعات شخصی
    national_id = Column(String(20), unique=True, nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # زمان‌ها
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # روابط
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlist_items = relationship("Product", secondary=wishlist, back_populates="wishlisted_by")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # emoji یا icon name
    
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)  # JSON string
    
    # قیمت‌گذاری
    base_price = Column(DECIMAL(15, 0), nullable=False)
    sale_price = Column(DECIMAL(15, 0), nullable=True)
    discount_percentage = Column(Float, default=0)
    
    # موجودی
    stock = Column(Integer, default=0)
    sku = Column(String(100), unique=True, nullable=True)
    
    # تصاویر
    main_image = Column(String(500), nullable=True)
    images = Column(Text, nullable=True)  # JSON array of image URLs
    
    # دسته‌بندی
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="products")
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_presale = Column(Boolean, default=False)
    presale_deadline = Column(DateTime, nullable=True)
    
    # زمان‌ها
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    wishlisted_by = relationship("User", secondary=wishlist, back_populates="wishlist_items")
    
    def __repr__(self):
        return f"<Product {self.name}>"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="orders")
    
    # آدرس تحویل
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_phone = Column(String(20), nullable=False)
    
    # مالی
    subtotal = Column(DECIMAL(15, 0), nullable=False)
    tax = Column(DECIMAL(15, 0), default=0)
    shipping_cost = Column(DECIMAL(15, 0), default=0)
    total_amount = Column(DECIMAL(15, 0), nullable=False)
    
    # وضعیت سفارش
    class OrderStatus(str, enum.Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        PROCESSING = "processing"
        SHIPPED = "shipped"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"
    
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # پرداخت
    class PaymentStatus(str, enum.Enum):
        UNPAID = "unpaid"
        PAID = "paid"
        REFUNDED = "refunded"
        FAILED = "failed"
    
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)
    payment_method = Column(String(50), nullable=True)  # bank, ton, installment
    payment_transaction_id = Column(String(255), nullable=True)
    
    # یادداشت‌ها
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # زمان‌ها
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # روابط
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    timeline = relationship("OrderTimeline", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    quantity = Column(Integer, default=1)
    unit_price = Column(DECIMAL(15, 0), nullable=False)
    total_price = Column(DECIMAL(15, 0), nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem {self.product_id} x{self.quantity}>"


class OrderTimeline(Base):
    __tablename__ = "order_timeline"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    
    class TimelineEventType(str, enum.Enum):
        CREATED = "created"
        CONFIRMED = "confirmed"
        PAYMENT_RECEIVED = "payment_received"
        PROCESSING = "processing"
        SHIPPED = "shipped"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"
    
    event_type = Column(Enum(TimelineEventType), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("Order", back_populates="timeline")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    verified_purchase = Column(Boolean, default=False)
    
    helpful_count = Column(Integer, default=0)
    unhelpful_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review {self.product_id} by {self.user_id}>"


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    
    amount = Column(DECIMAL(15, 0), nullable=False)
    currency = Column(String(10), default="IRR")
    
    payment_method = Column(String(50), nullable=False)  # bank_transfer, ton, installment
    gateway = Column(String(100), nullable=True)  # gateway name
    
    transaction_id = Column(String(255), unique=True, nullable=True)
    reference_code = Column(String(255), unique=True, nullable=True)
    
    class TransactionStatus(str, enum.Enum):
        PENDING = "pending"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
    
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    response_data = Column(Text, nullable=True)  # JSON response from gateway
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<PaymentTransaction {self.transaction_id}>"


class PresaleConfiguration(Base):
    __tablename__ = "presale_config"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    total_capacity = Column(Integer, nullable=False)
    registered_count = Column(Integer, default=0)
    deadline = Column(DateTime, nullable=False)
    down_payment = Column(DECIMAL(15, 0), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Page(Base):
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    content = Column(Text, nullable=False)
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(String(500), nullable=True)
    seo_keywords = Column(String(500), nullable=True)
    
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Page {self.slug}>"


class Blog(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(String(500), nullable=True)
    featured_image = Column(String(500), nullable=True)
    
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(String(500), nullable=True)
    
    is_published = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
