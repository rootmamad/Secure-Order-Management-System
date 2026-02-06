from fastapi import FastAPI , Depends,APIRouter
from  pydantic import BaseModel
from database import get_session, Base, engine
from models import Items
from sqlalchemy.orm import Session 
from dependencies import JWTBearer
from auth import router 

app = FastAPI()

access = JWTBearer()
app.include_router(router)

class Item(BaseModel):
    name: str
    price: float
    quantity: int


    

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
async def read_items(session: Session=Depends(get_session)) -> list[Item]:
    items = session.query(Items).all()
    return items

@app.post("/cancel/",response_model=Item)
async def cancel(item_id: int, session: Session=Depends(get_session)) -> Item:
    item = session.get(Items, item_id)
    if item:
        session.delete(item)
    return item
