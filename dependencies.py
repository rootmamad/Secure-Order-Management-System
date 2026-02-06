from fastapi import status,Request
from fastapi.security import HTTPBearer

class JWTBearer(HTTPBearer):
    async def __call__(self, request:Request):
        credentials = await super().__call__(request)
        if credentials:
            token = credentials.credentials
            # Here you would add your JWT validation logic
            if token == "valid_token":  # Placeholder for actual validation
                return credentials
            #checking is not refresh token
            # # if is_refresh_token(token):
            # 
            # 
            #  
        raise status.HTTP_403_FORBIDDEN(status_code=403, detail="Invalid or missing token")