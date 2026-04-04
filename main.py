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
from routers import items, orders,users
app = FastAPI()

access = JWTBearer()
app.include_router(router)
app.include_router(items.router)      
app.include_router(orders.router) 
app.include_router(users.router) 


@app.exception_handler(Exception)
async def handle_error(request:Request,exception:Exception):
    print(f"CRITICAL ERROR on {request.url.path}: {exception}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

def create_db_and_tables():
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")