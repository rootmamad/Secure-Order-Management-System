from fastapi import FastAPI , Depends ,HTTPException, status,Request
from fastapi.responses import JSONResponse
from  pydantic import BaseModel
from database import get_session, Base, engine
from models import Items,Users ,UserItem
from sqlalchemy.orm import Session , joinedload
from dependencies import JWTBearer,require_admin_role,require_staff_role
from auth import router 

app = FastAPI()

access = JWTBearer()
app.include_router(router)

@app.exception_handler(Exception)
async def handle_error(request:Request,exception:Exception):
    print(f"CRITICAL ERROR on {request.url.path}: {exception}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )




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
    

class OrderResponse(BaseModel):
    username: str
    item : str
    quantity: int

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




def create_db_and_tables():
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")







@app.post("/create/" , response_model=Item)
def create_item(item: Item, session: Session=Depends(get_session),dependency=Depends(require_staff_role)) -> Item:
    db_item  = Items(**item.model_dump())
    session.add(db_item)

    session.flush()
    session.refresh(db_item)
    return db_item

@app.get("/item/{item_id}", response_model=Item)
def read_item(item_id: int, session: Session=Depends(get_session),dependency=Depends(access)) -> Item:

    item = session.get(Items, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول موجود نیست")

    return item


@app.get("/items/", response_model=list[Item])
def read_items(limit:int=10, offset:int =0 ,session: Session=Depends(get_session), dependency=Depends(access)) -> list[Item]:
    items = session.query(Items).offset(offset).limit(limit).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" محصولی موجود نیست")

    return items

@app.post("/item/{item_id}/buy")
def buy(item_id:int , quantity:int , session:Session=Depends(get_session),current_user=Depends(access)):
    user = session.query(Users).filter(Users.id == current_user["user_id"]).with_for_update().first()
    item = session.query(Items).filter(Items.id == item_id).with_for_update().first()

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
    
    exist_item = session.query(UserItem).filter_by(item_id=item_id,user_id = user.id).with_for_update().first()
    if exist_item:
        exist_item.quantity += quantity
    else:
        transaction = UserItem(item_id=item_id,user_id=user.id,quantity=quantity,user=user,item=item)
        session.add(transaction)
    session.flush()
    return {"message": f"تعداد {quantity} عدد از {item.name} به لیست خریدهای شما اضافه شد"}


@app.post("/delete/",response_model=Item)
def delete(item_id: int, session: Session=Depends(get_session),dependency=Depends(require_staff_role)) -> Item:
    item = session.get(Items, item_id)
    if item:
        session.delete(item)
    return item

@app.get("/users/", response_model=list[UserResponse]) 
def get_all_users(session: Session = Depends(get_session),current_user: dict = Depends(require_admin_role)):
    users = session.query(Users).all()
    return users

@app.patch("/users/role/{user_id}")
def update_role(user_id:int,request:RoleUpdateRequest,session:Session =Depends(get_session),current_user:dict=Depends(require_admin_role)):    
    if request.role not in ["customer","staff","admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="role is invalid.")
    user = session.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found.")
    user.role = request.role
    session.flush()
    return {"message": f"User {user.username} is now a {request.role}"}

@app.get("/myitem",response_model=list[MyItemResponse])
def myitem(session: Session=Depends(get_session),current_user=Depends(access)) :
    items = session.query(UserItem).options(joinedload(UserItem.item)).filter(UserItem.user_id == current_user["user_id"]).all()
    
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" محصولی موجود نیست")

    return items

@app.post("/item/{item_id}/return")
def return_item(item_id:int , quantity:int, session:Session = Depends(get_session),current_user = Depends(access)):
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
def get_order(order_id:int,session:Session = Depends(get_session),current_user=Depends(access)) -> OrderResponse:
    order = session.query(UserItem).filter(UserItem.id == order_id)

    if current_user["role"] == "customer":
        order = order.filter(UserItem.user_id == current_user["user_id"])
        
    order = order.first()

    if not  order:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="سفارش موجود نیست.")
    
    return {"username": order.user.username, "item": order.item.name, "quantity": order.quantity}