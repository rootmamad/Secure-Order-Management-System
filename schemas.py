from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserResponse(BaseModel):
    id:int
    username: str
    full_name:str
    balance:int
    role:str

    class Config:
        from_attributes = True

class UserBasicInfo(BaseModel):
    username: str
    class Config:
        from_attributes = True
class UserResponse(BaseModel):
    id:int
    username: str
    full_name:str
    balance:int
    role:str

    class Config:
        from_attributes = True

class RoleUpdateRequest(BaseModel):
    role: str


class Item(BaseModel):
    name: str
    price: float
    quantity: int
    class Config:
        from_attributes = True

class ItemResponse(Item):
    id:int 


class ItemInfo(BaseModel):
    name: str
    price: int

    class Config:
        from_attributes = True

class MyItemResponse(BaseModel):
    item_id: int
    quantity: int
    item: ItemInfo 

    class Config:
        from_attributes = True





class UserBasicInfo(BaseModel):
    username: str
    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    item_id: int
    quantity: int
    price_at_buy: int
    item: ItemInfo  

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id:int
    user: UserBasicInfo
    created_at:datetime
    kind:str
    status:str
    total_amount :int 
    items : List[OrderItemResponse]
    

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    full_name: str | None = None


class UserCreate(UserBase):
    password: str
    balance: int



class UserRead(UserBase):
    id: int


class UserInDB(UserBase):
    hashed_password: str    


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LoginResponse(BaseModel):
    token: Token
    user: UserRead

class UserLogin(BaseModel):
    username: str
    password: str