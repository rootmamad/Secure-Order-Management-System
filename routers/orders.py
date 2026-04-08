from fastapi import   Depends ,HTTPException, status,APIRouter,Request
from database import get_session
from sqlalchemy.orm import Session 
from models import Order,OrderItem,Items,Users
from sqlalchemy import func,case 
from schemas import MyItemResponse,OrderResponse
from dependencies import JWTBearer
from rate_limiter import limiter

access = JWTBearer()
router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"]
)


@router.post("/item/{item_id}/add-to-cart")
@limiter.limit("20/minute")
def add_to_cart(request:Request,item_id:int , quantity:int , session:Session=Depends(get_session),current_user=Depends(access)):
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





@router.get("/myitem",response_model=list[MyItemResponse])
@limiter.limit("5/minute")
def myitem(request:Request,session: Session=Depends(get_session),current_user=Depends(access)) :


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

@router.post("/item/{item_id}/return")
@limiter.limit("5/minute")
def return_item(request:Request,item_id:int , quantity:int, session:Session = Depends(get_session),current_user = Depends(access)):
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

@router.get("/order/{order_id}",response_model=OrderResponse)
@limiter.limit("100/minute")
def get_order(request:Request,order_id:int,session:Session = Depends(get_session),current_user=Depends(access)) -> OrderResponse:
    order = session.query(Order).filter(Order.id == order_id)

    if current_user["role"] == "customer":
        order = order.filter(Order.user_id == current_user["user_id"])
    order = order.first()

    if not  order:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="سفارش موجود نیست.")
    
    return order

@router.post("/order/{order_id}/checkout")
@limiter.limit("5/minute")
def checkout(request:Request,order_id:int,session:Session=Depends(get_session),current_user=Depends(access)):
    order = session.query(Order).with_for_update().filter(Order.id == order_id)
    
    
    if current_user["role"] == "customer":
        order = order.filter(Order.user_id == current_user["user_id"])

    order = order.first()    
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="order not found.")
    

    
    if order.status == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This order has already been completed.")
    
    user = session.query(Users).with_for_update().filter(Users.id == order.user_id).first()
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



@router.patch("/order/{order_id}/cancel")
@limiter.limit("5/minute")
async def cancel(request:Request,order_id:int,session:Session=Depends(get_session),current_user=Depends(access)):
    order = session.query(Order).filter(Order.id == order_id).with_for_update()

    if current_user["role"] == "customer":
        order = order.filter(Order.user_id == current_user["user_id"])

    order= order.first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="order not found.")
    

    
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="This order has already been completed or canceled.")
    order.status = "canceled"
    session.flush()
    return {"message": "سفارش با موفقیت لغو شد."}
