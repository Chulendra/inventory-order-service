from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0, description="Price must be greater than zero")
    stock_quantity: int = Field(ge=0, description="Stock cannot be negative")

class ProductCreate(ProductBase):
    pass  # Used for POST /products

class Product(ProductBase):
    id: int

    class ConfigDict:
        from_attributes = True # Allows Pydantic to read SQLAlchemy models


# --- Order Item Schemas ---
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be at least 1")

class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_price: float

    class ConfigDict:
        from_attributes = True

# --- Order Status Enum ---
class OrderStatus(str, Enum):
    PENDING = "Pending"
    SHIPPED = "Shipped"
    CANCELED = "Canceled"

# --- Order Schemas ---
class OrderBase(BaseModel):
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(BaseModel):
    # This is what the user sends: a list of items to buy
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    created_at: datetime
    items: List[OrderItem] # Nested list of items

    class ConfigDict:
        from_attributes = True