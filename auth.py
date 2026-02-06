import jwt
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from utils import create_hash,create_token, verify_hash, verify_token
from models import Users, RefreshTokens
from database import get_session

secret_key = "rootmamad06"
algorithm = "HS256"
router = APIRouter(prefix="/auth", tags=["auth"])


class UserBase(BaseModel):
    username: str
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserInDB(UserBase):
    hashed_password: str    


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LoginResponse(BaseModel):
    token: Token
    user: UserRead

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register/", response_model=LoginResponse)
async def register(user: UserCreate, session: Session = Depends(get_session)) -> LoginResponse:


    if session.query(Users).filter(Users.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    hashed_password = await create_hash(user.password)
    db_user = Users(username=user.username, full_name=user.full_name, hashed_password=hashed_password)
    session.add(db_user)
    session.flush()
    session.refresh(db_user)


    refresh_token = await create_token({"user_id": db_user.id,"username": db_user.username,"is_refresh": True}, secret_key, algorithm)
    db_refresh_token = RefreshTokens(user_id=db_user.id, token=refresh_token)
    session.add(db_refresh_token)   
    session.flush()
    session.refresh(db_refresh_token)
    access_token = await create_token({"user_id": db_user.id,"username": db_user.username,"is_refresh": False}, secret_key, algorithm)  
    return {
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "user": db_user  
    } 


@router.post("/login/", response_model=LoginResponse)
async def login(user: UserLogin, session: Session = Depends(get_session)) -> LoginResponse:
    db_user = session.query(Users).filter(Users.username == user.username).first()

    if not db_user or not await verify_hash(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    last_refresh_token = session.query(RefreshTokens).filter(RefreshTokens.user_id == db_user.id).order_by(RefreshTokens.id.desc()).first()
    if last_refresh_token:
        session.delete(last_refresh_token)
        session.flush()

    refresh_token = await create_token({"user_id": db_user.id,"username": db_user.username,"is_refresh": True}, secret_key, algorithm)
    db_refresh_token = RefreshTokens(user_id=db_user.id, token=refresh_token)
    session.add(db_refresh_token)   
    session.flush()
    session.refresh(db_refresh_token)
    access_token = await create_token({"user_id": db_user.id,"username": db_user.username,"is_refresh": False}, secret_key, algorithm)  
    return {
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "user": db_user  
    }

@router.post("/refresh/", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, session: Session = Depends(get_session)) -> Token:
    try:
        payload = jwt.decode(request.refresh_token, secret_key, algorithms=[algorithm])
        if not payload.get("is_refresh"):
            raise HTTPException(status_code=401, detail="این اکسس توکنه، رفرش توکن بده!")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="توکن نامعتبر یا منقضی شده")

    old_refresh_token = session.query(RefreshTokens).filter(RefreshTokens.token == request.refresh_token).first()
    if not old_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user = session.query(Users).filter(Users.id == old_refresh_token.user_id).first()
    if not user:   
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    new_access_token = await create_token({"user_id": user.id,"username": user.username,"is_refresh": False}, secret_key, algorithm)  
    session.delete(old_refresh_token)
    session.flush()
    new_refresh_token = await create_token({"user_id": user.id,"username": user.username,"is_refresh": True}, secret_key, algorithm)
    db_refresh_token = RefreshTokens(user_id=user.id, token=new_refresh_token)
    session.add(db_refresh_token)
    session.flush()
    session.refresh(db_refresh_token)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }