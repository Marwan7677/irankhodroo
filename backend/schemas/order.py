"""
Order Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    discount_percentage: float
    subtotal: float
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    # Shipping
    shipping_address: str = Field(..., min_length=10)
    shipping_city: str = Field(..., min_length=2)
    shipping_postal_code: str = Field(..., min_length=5)
    shipping_phone: str = Field(..., min_length=10, max_length=20)
    
    # Payment
    payment_method: str = Field(..., regex="^(card|ton|installment)$")
    
    # Installment
    installment_months: Optional[int] = Field(None, ge=1, le=60)
    
    # TON
    ton_wallet_address: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: str
    payment_status: str
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

class OrderDetail(OrderResponse):
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_phone: str
    shipping_cost: float
    installment_months: Optional[int]
    ton_transaction_hash: Optional[str]
    notes: Optional[str]
    updated_at: datetime
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]

class OrderStatusUpdate(BaseModel):
    status: str = Field(..., regex="^(pending|confirmed|processing|shipped|delivered|cancelled|returned)$")
    notes: Optional[str] = None
