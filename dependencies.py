from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from auth import verify_token, secret_key, algorithm 

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            token = credentials.credentials 
            
            try:
                payload = await verify_token(token, secret_key, [algorithm])
                
                if payload.get("is_refresh"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, 
                        detail="این رفرش توکنه، اکسس توکن معتبر بفرست"
                    )
                
                return payload 
                
            except HTTPException as e:
                raise e
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="توکن نامعتبر است"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="توکن ارسال نشده است"
            )