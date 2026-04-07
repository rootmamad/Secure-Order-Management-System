from fastapi import FastAPI , status,Request
from fastapi.responses import JSONResponse
from database import Base, engine
from dependencies import JWTBearer
from auth import router 
from routers import items, orders,users
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - PATH: %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI()

access = JWTBearer()
app.include_router(router)
app.include_router(items.router)      
app.include_router(orders.router) 
app.include_router(users.router) 


@app.exception_handler(Exception)
async def handle_error(request:Request,exception:Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exception}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

def create_db_and_tables():
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")

