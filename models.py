from sqlalchemy import Table, Column, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship


class UserItem(Base):
    __tablename__ = "user_items"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("Items.id"), primary_key=True)
    quantity = Column(Integer, default=1)
    
    user = relationship("Users", back_populates="purchased_items")
    item = relationship("Items", back_populates="buyers")


class Items(Base):
    __tablename__ = "Items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Integer)
    buyers = relationship("UserItem", back_populates="item")

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    hashed_password = Column(String)
    balance = Column(Integer,default=0)
    purchased_items = relationship("UserItem", back_populates="user")

    
class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    