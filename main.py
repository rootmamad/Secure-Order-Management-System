from fastapi import FastAPI , Depends
from  pydantic import BaseModel
from database import SessionLocal, Base, engine
from typing import Annotated
from models import Items
from sqlalchemy.orm import Session 

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    quantity: int

class User(BaseModel):
    username: str
    full_name: str | None = None
    

def create_db_and_tables():
    Base.metadata.create_all(engine)


def get_session():
    db =SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/items/" , response_model=Item)
def create_hero(hero: Item, session: Session=Depends(get_session)) -> Item:
    db_hero  = Items(**hero.model_dump())
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int, session: Session=Depends(get_session)) -> Item:
    item = session.get(Items, item_id)
    return item


@app.get("/items/", response_model=list[Item])
async def read_items(session: Session=Depends(get_session)) -> list[Item]:
    items = session.query(Items).all()
    return items