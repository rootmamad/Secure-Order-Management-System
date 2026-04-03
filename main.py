from fastapi import FastAPI , Depends ,HTTPException, status,Request
from fastapi.responses import JSONResponse
from  pydantic import BaseModel
from database import get_session, Base, engine
from models import Items,Users ,Order,OrderItem
from sqlalchemy.orm import Session 
from dependencies import JWTBearer,require_admin_role,require_staff_role
from auth import router 
from typing import List
from datetime import datetime
from sqlalchemy import func, case

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

@app.post("/item/{item_id}/add-to-cart")
def add_to_cart(item_id:int , quantity:int , session:Session=Depends(get_session),current_user=Depends(access)):
    user = session.query(Users).filter(Users.id == current_user["user_id"]).with_for_update().first()
    item = session.query(Items).filter(Items.id == item_id).with_for_update().first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول موجود نیست")

    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="موجودی نمیتواند منفی باشد.")
    
    if item.quantity < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"موجودی کالا کافی نیست. موجودی فعلی: {item.quantity}")
    
    if quantity * item.price > user.balance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="اعتبار حساب کافی نیست.")

    order = session.query(Order).filter_by(user_id = user.id, status="pending",kind="buy").first()
    if not order:
        order = Order(user_id = user.id, status="pending",kind="buy")
        session.add(order)
        session.flush()

    order.total_amount += quantity*item.price
    
    exist_order_item = session.query(OrderItem).filter(OrderItem.order_id==order.id,OrderItem.item_id == item_id).first()
    if exist_order_item:
        exist_order_item.quantity += quantity
    else:
        new_order_item = OrderItem(
                                order_id=order.id, 
                                item_id=item.id, 
                                quantity=quantity,
                                price_at_buy=item.price
                                    )

        session.add(new_order_item)
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


    calculator = func.sum(
        case((Order.kind=="buy",OrderItem.quantity),(Order.kind=="return",-OrderItem.quantity),else_=0)
    )
    results = session.query(
    OrderItem.item_id,
    calculator.label("quantity"),
    Items
    ).join(
    Order, Order.id == OrderItem.order_id
    ).join(Items,Items.id == OrderItem.item_id).filter(Order.status=="completed",Order.user_id==current_user["user_id"]).group_by(OrderItem.item_id,Items.id).having(calculator>0).all()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" محصولی موجود نیست")
    items = []
    for row in results:
        items.append({"item_id": row.item_id,
        "quantity": row.quantity,
        "item":row.Items}
        )
    return items

@app.post("/item/{item_id}/return")
def return_item(item_id:int , quantity:int, session:Session = Depends(get_session),current_user = Depends(access)):
    user = session.query(Users).with_for_update().get(current_user["user_id"])
    myitems = myitem(session=session,current_user=current_user)
    item = session.query(Items).filter(Items.id==item_id).with_for_update().first()
    
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول موجود نیست")
    myitems_ = [item["item"] for item in myitems]
    quantities = [item["quantity"] for item in myitems]
    if item not in myitems_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول در لیست خرید شما وجود ندارد")
    
    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="موجودی نمیتواند منفی باشد.")
    
    if quantity > quantities[myitems_.index(item)]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"شما فقط {quantities[myitems_.index(item)]} عدد از این محصول را خریداری کرده اید.")
    order = Order(user_id=user.id,status="completed",kind="return")
    session.add(order)
    session.flush()
    session.refresh(order)
    order_item = OrderItem(order_id=order.id,item_id=item.id,quantity=quantity,price_at_buy=item.price)
    
    
    session.add(order_item)
    session.flush()
    user.balance += quantity * item.price
    item.quantity += quantity
    order.total_amount += quantity * item.price
    session.flush()
    return {"message": f"تعداد {quantity} عدد از {item.name} با موفقیت مرجوع شد."}


@app.get("/order/{order_id}",response_model=OrderResponse)
def get_order(order_id:int,session:Session = Depends(get_session),current_user=Depends(access)) -> OrderResponse:
    order = session.query(Order).filter(Order.id == order_id)

    if current_user["role"] == "customer":
        order = order.filter(Order.user_id == current_user["user_id"])
    order = order.first()

    if not  order:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="سفارش موجود نیست.")
    
    return order


@app.post("/order/{order_id}/checkout")
def checkout(order_id:int,session:Session=Depends(get_session),current_user=Depends(access)):
    order = session.query(Order).with_for_update().filter(Order.id == order_id)
    user = session.query(Users).with_for_update().filter(Users.id == current_user["user_id"]).first()
    
    if current_user["role"] == "customer":
        order = order.filter(Order.user_id == current_user["user_id"])

    order = order.first()    
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="order not found.")
    

    
    if order.status == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This order has already been completed.")
    
    
    if order.total_amount > user.balance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Insufficient balance to complete the checkout.")
    
    order_items = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    item_ids = [order_item.item_id for order_item in order_items]
    items = session.query(Items).filter(Items.id.in_(item_ids)).with_for_update().all()

    items_dict = {item.id : item for item in items}

    for item_ in order_items:

        item = items_dict.get(item_.item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Item with ID {item_.item_id} no longer exists.")
        if item_.quantity >  item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Insufficient stock for '{item.name}'. Only {item.quantity} remaining (requested: {item_.quantity}).")
        
        item.quantity -= item_.quantity
    user.balance -= order.total_amount
    order.status = "completed"

    return {"message":"Order successfully completed."}