from sqlalchemy import DateTime, Column, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String, default="pending")
    kind = Column(String, default="buy")

    user = relationship("Users", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "orderitems"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer, ForeignKey("Items.id"))
    quantity = Column(Integer, nullable=False)
    price_at_buy = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    item = relationship("Items", back_populates="order_items")


class Items(Base):
    __tablename__ = "Items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Integer)
    order_items = relationship("OrderItem", back_populates="item")


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    hashed_password = Column(String)
    balance = Column(Integer, default=0)
    orders = relationship("Order", back_populates="user")
    role = Column(String, default="customer")


class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String, index=True)
    detail = Column(String, index=True)
    time = Column(DateTime, default=datetime.now)
