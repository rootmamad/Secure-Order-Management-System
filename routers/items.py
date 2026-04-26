from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from database import get_session
from models import Items
from dependencies import require_staff_role
from schemas import Item,ItemResponse
from dependencies import JWTBearer
from rate_limiter import limiter

access = JWTBearer()


router = APIRouter(
    prefix="/api/v1/items",
    tags=["Items"]
)


@router.post("/create/" , response_model=ItemResponse)
def create_item(item: Item, session: Session=Depends(get_session),dependency=Depends(require_staff_role)) -> Item:
    db_item  = Items(**item.model_dump())
    session.add(db_item)

    session.flush()
    session.refresh(db_item)
    return db_item
@router.get("/item/{item_id}", response_model=Item)
@limiter.limit("100/minute")
def read_item(request:Request,item_id: int, session: Session=Depends(get_session),dependency=Depends(access)) -> Item:

    item = session.get(Items, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="این محصول موجود نیست")

    return item


@router.get("/items/", response_model=list[Item])
@limiter.limit("30/minute")
def read_items(request:Request,limit:int=10, offset:int =0 ,session: Session=Depends(get_session), dependency=Depends(access)) -> list[Item]:
    items = session.query(Items).offset(offset).limit(limit).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" محصولی موجود نیست")

    return items
@router.post("/delete/",response_model=Item)
def delete(item_id: int, session: Session=Depends(get_session),dependency=Depends(require_staff_role)) -> Item:
    item = session.get(Items, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="چنین محصولی موجود نیست")

    session.delete(item)
    
    return item
