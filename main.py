from fastapi import FastAPI , Depends ,HTTPException, status
from  pydantic import BaseModel
from database import get_session, Base, engine
from models import Items,Users ,UserItem
from sqlalchemy.orm import Session , joinedload
from dependencies import JWTBearer
from auth import router 
from typing import List

app = FastAPI()

access = JWTBearer()
app.include_router(router)

class Item(BaseModel):
    name: str
    price: float
    quantity: int


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
    

class OrderResponse(BaseModel):
    username: str
    item : str
    quantity: int

    class Config:
        from_attributes = True





def create_db_and_tables():
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")





@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/create/" , response_model=Item)
def create_hero(hero: Item, session: Session=Depends(get_session)) -> Item:
    db_hero  = Items(**hero.model_dump())
    session.add(db_hero)

    session.flush()
    session.refresh(db_hero)
    return db_hero

@app.get("/item/{item_id}", response_model=Item)
async def read_item(item_id: int, session: Session=Depends(get_session),dependency=Depends(access)) -> Item:
    item = session.get(Items, item_id)
    return item


@app.get("/items/", response_model=list[Item])
async def read_items(session: Session=Depends(get_session),dependency=Depends(access)) -> list[Item]:
    items = session.query(Items).all()
    return items

@app.post("/item/{item_id}/buy")
async def buy(item_id:int , quantity:int , session:Session=Depends(get_session),current_user=Depends(access)):
    user = session.query(Users).filter(Users.id == current_user["user_id"]).first()
    item = session.query(Items).filter(Items.id == item_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول موجود نیست")

    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="موجودی نمیتواند منفی باشد.")
    
    if item.quantity < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"موجودی کافی نیست. موجودی فعلی: {item.quantity}")
    
    if quantity * item.price > user.balance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="موجودی کافی نیست.")

    user.balance -= quantity * item.price
    item.quantity -= quantity
    
    exist_item = session.query(UserItem).filter_by(item_id=item_id,user_id = user.id).first()
    if exist_item:
        exist_item.quantity += quantity
    else:
        transaction = UserItem(item_id=item_id,user_id=user.id,quantity=quantity,user=user,item=item)
        session.add(transaction)
    session.flush()
    return {"message": f"تعداد {quantity} عدد از {item.name} به لیست خریدهای شما اضافه شد"}


@app.post("/delete/",response_model=Item)
async def delete(item_id: int, session: Session=Depends(get_session)) -> Item:
    item = session.get(Items, item_id)
    if item:
        session.delete(item)
    return item


@app.get("/myitem",response_model=list[MyItemResponse])
async def myitem(session: Session=Depends(get_session),current_user=Depends(access)) :
    items = session.query(UserItem).options(joinedload(UserItem.item)).filter(UserItem.user_id == current_user["user_id"]).all()
    return items

@app.post("/item/{item_id}/return")
async def return_item(item_id:int , quantity:int, session:Session = Depends(get_session),current_user = Depends(access)):
    user = session.query(Users).get(current_user["user_id"])
    item = session.query(Items).filter(Items.id==item_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول موجود نیست")
    
    exist_order = session.query(UserItem).filter_by(item_id=item_id,user_id=user.id).first()
    if not exist_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول در لیست خرید شما وجود ندارد")

    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="موجودی نمیتواند منفی باشد.")
    
    if quantity > exist_order.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"شما فقط {exist_order.quantity} عدد از این محصول را خریداری کرده اید.")
    
    user.balance += quantity * item.price
    item.quantity += quantity
    exist_order.quantity -= quantity
    if exist_order.quantity == 0:
        session.delete(exist_order)
    session.flush()
    return {"message": f"تعداد {quantity} عدد از {item.name} با موفقیت مرجوع شد."}


@app.get("/order/{order_id}",response_model=OrderResponse)
async def get_order(order_id:int,session:Session = Depends(get_session),current_user=Depends(access)) -> OrderResponse:
    order = session.query(UserItem).filter(
    UserItem.id == order_id, 
    UserItem.user_id == current_user["user_id"]
    ).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="چنین سفارشی وجود ندارد.")

    return {"username": order.user.username, "item": order.item.name, "quantity": order.quantity} 