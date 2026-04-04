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

