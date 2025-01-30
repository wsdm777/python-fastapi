from typing import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi_users.authentication import JWTStrategy
from jose import jwt
from src.auth.schemas import UserTokenInfo
from src.config import SECRET
from src.databasemodels import User
from fastapi_users.jwt import generate_jwt
from fastapi import status


class CustomJWTStrategy(JWTStrategy):
    async def write_token(self, user: User) -> str:

        user_data = {}
        user_data["sub"] = str(user.id)
        user_data["email"] = user.email
        user_data["admin"] = user.is_superuser

        return generate_jwt(
            user_data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )


def get_user_email(request: Request, superuser: bool = False) -> dict:
    token = request.cookies.get("authcook")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JWT token"
        )

    id = payload.get("sub")
    email = payload.get("email")
    is_superuser = payload.get("admin")
    return UserTokenInfo(id=id, email=email, is_superuser=is_superuser)


def get_current_user(request: Request) -> UserTokenInfo:
    return get_user_email(request)


def get_current_superuser(request: Request) -> UserTokenInfo:
    user = get_user_email(request)
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user
