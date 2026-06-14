"""
Product Model - مدل محصول
"""
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0)
    discount_price = Column(Float, nullable=True)
    
    # Product Details
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    sku = Column(String(100), unique=True, nullable=True)
    
    # Specifications (JSON-like stored as text, better in production use JSON column)
    engine_cc = Column(String(50), nullable=True)  # e.g., "1600"
    transmission = Column(String(50), nullable=True)  # دستی, اتوماتیک
    fuel_type = Column(String(50), nullable=True)  # بنزینی, گاز, برقی
    seats = Column(Integer, default=5)
    color = Column(String(50), nullable=True)
    
    # Inventory
    stock = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_presale = Column(Boolean, default=False)
    
    # Ratings
    average_rating = Column(Float, default=0)
    review_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    wishlists = relationship("Wishlist", back_populates="product", cascade="all, delete-orphan")

class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    # Relationships
    product = relationship("Product", back_populates="images")
