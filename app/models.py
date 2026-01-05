from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime, UTC
import enum

class Base(DeclarativeBase):
    pass

class Status(enum.Enum):
    PENDING = "Pending"
    SHIPPED = "Shipped"
    CANCELED = "Canceled"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)

    # Relationship to the items in an order
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(Status), default=Status.PENDING)
    created_at = Column(DateTime, default=datetime.now(UTC))

    # Relationship to the items within this specific order
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
