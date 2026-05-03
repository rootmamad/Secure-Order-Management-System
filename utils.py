from datetime import timedelta, datetime
import jwt
from passlib.hash import pbkdf2_sha256
from fastapi import HTTPException, status, Request
from slowapi.util import get_remote_address
from config import settings


def create_hash(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_hash(password: str, hash: str) -> bool:
    return pbkdf2_sha256.verify(password, hash)


def create_token(data: dict, secret_key: str, algorithm: str) -> str:
    to_encode = data.copy()

    if data.get("is_refresh"):
        expire = datetime.utcnow() + timedelta(days=7)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_token(token: str, secret_key: str, algorithms: list[str]) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def get_user_id(request: Request):

    header = request.headers.get("Authorization")
    if header and header.startswith("Bearer "):
        token = header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.secret_key, [settings.algorithm])
            user_id = payload.get("user_id")

            return f"user:{user_id}"

        except jwt.PyJWTError:
            pass

    return get_remote_address(request)
