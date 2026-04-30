import jwt
from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from utils import create_hash,create_token, verify_hash, verify_token
from models import Users, RefreshTokens
from database import get_session
from rate_limiter import limiter
from schemas import LoginResponse,UserCreate,UserLogin,Token,RefreshTokenRequest
from config import settings


router = APIRouter(prefix="/auth", tags=["auth"])




@router.post("/register/", response_model=LoginResponse)
@limiter.limit("15/minute")
def register(request:Request,user: UserCreate, session: Session = Depends(get_session)) -> LoginResponse:


    if session.query(Users).filter(Users.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    hashed_password =  create_hash(user.password)
    db_user = Users(username=user.username, full_name=user.full_name, hashed_password=hashed_password,balance=user.balance)
    session.add(db_user)
    session.flush()
    session.refresh(db_user)


    refresh_token =  create_token({"user_id": db_user.id,"username": db_user.username,"is_refresh": True}, settings.secret_key, settings.algorithm)
    db_refresh_token = RefreshTokens(user_id=db_user.id, token=refresh_token)
    session.add(db_refresh_token)   
    session.flush()
    session.refresh(db_refresh_token)
    access_token =  create_token({"user_id": db_user.id,"username": db_user.username,"role": db_user.role,"is_refresh": False}, settings.secret_key, settings.algorithm)  
    return {
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "user": db_user  
    } 


@router.post("/login/", response_model=LoginResponse)
@limiter.limit("15/minute")
def login(request:Request,user: UserLogin, session: Session = Depends(get_session)) -> LoginResponse:
    db_user = session.query(Users).filter(Users.username == user.username).first()

    if not db_user or not  verify_hash(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    last_refresh_token = session.query(RefreshTokens).filter(RefreshTokens.user_id == db_user.id).order_by(RefreshTokens.id.desc()).first()
    if last_refresh_token:
        session.delete(last_refresh_token)
        session.flush()

    refresh_token =  create_token({"user_id": db_user.id,"username": db_user.username,"is_refresh": True}, settings.secret_key, settings.algorithm)
    db_refresh_token = RefreshTokens(user_id=db_user.id, token=refresh_token)
    session.add(db_refresh_token)   
    session.flush()
    session.refresh(db_refresh_token)
    access_token =  create_token({"user_id": db_user.id,"username": db_user.username,"role": db_user.role,"is_refresh": False}, settings.secret_key, settings.algorithm)  
    return {
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "user": db_user  
    }
@router.post("/refresh/", response_model=Token)
@limiter.limit("5/minute")
def refresh_token(request:Request,request_: RefreshTokenRequest, session: Session = Depends(get_session)) -> Token:
    try:
        payload = jwt.decode(request_.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if not payload.get("is_refresh"):
            raise HTTPException(status_code=401, detail="این اکسس توکنه، رفرش توکن بده!")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="توکن نامعتبر یا منقضی شده")

    old_refresh_token = session.query(RefreshTokens).filter(RefreshTokens.token == request_.refresh_token).first()
    if not old_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user = session.query(Users).filter(Users.id == old_refresh_token.user_id).first()
    if not user:   
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    new_access_token =  create_token({"user_id": user.id,"username": user.username,"role": user.role,"is_refresh": False}, settings.secret_key, settings.algorithm)  
    session.delete(old_refresh_token)
    session.flush()
    new_refresh_token =  create_token({"user_id": user.id,"username": user.username,"is_refresh": True}, settings.secret_key, settings.algorithm)
    db_refresh_token = RefreshTokens(user_id=user.id, token=new_refresh_token)
    session.add(db_refresh_token)
    session.flush()
    session.refresh(db_refresh_token)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }