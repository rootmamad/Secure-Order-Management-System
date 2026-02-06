from datetime import timedelta,datetime
import jwt 
from passlib.hash import pbkdf2_sha256
from fastapi import HTTPException, status

async def create_hash(password: str) -> str:
    return pbkdf2_sha256.hash(password)   


async def verify_hash(password: str, hash: str) -> bool:
    return pbkdf2_sha256.verify(password, hash)   

async def create_token(data: dict, secret_key: str, algorithm: str) -> str:
    to_encode = data.copy()
    
    if data.get("is_refresh"):
        expire = datetime.utcnow() + timedelta(days=7)
    else:
        expire = datetime.utcnow() + timedelta(minutes=1)
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


async def verify_token(token: str, secret_key: str, algorithms: list[str]) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )
