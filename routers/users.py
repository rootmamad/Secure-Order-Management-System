from fastapi import   Depends ,HTTPException, status,APIRouter
from database import get_session
from sqlalchemy.orm import Session 
from models import Users 
from dependencies import require_admin_role
from schemas import UserResponse,RoleUpdateRequest
from dependencies import JWTBearer
access = JWTBearer()

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)


@router.get("/users/", response_model=list[UserResponse]) 
def get_all_users(offset:int=0,limit:int=10,session: Session = Depends(get_session),current_user: dict = Depends(require_admin_role)):
    users = session.query(Users).limit(limit).offset(offset).all()
    return users

@router.patch("/users/role/{user_id}")
def update_role(user_id:int,request:RoleUpdateRequest,session:Session =Depends(get_session),current_user:dict=Depends(require_admin_role)):    
    if request.role not in ["customer","staff","admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="role is invalid.")
    user = session.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found.")
    user.role = request.role
    session.flush()
    return {"message": f"User {user.username} is now a {request.role}"}