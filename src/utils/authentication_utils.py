from datetime import timedelta, datetime
from typing import Annotated

from decouple import config
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTClaimsError, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from starlette import status

from models.user_model import User

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/authentication/login")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = "HS256"


async def authenticate_user(db, email: str, password) -> User | bool:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password provided")
    return user


def create_jwt_token(user: User, expires_delta: timedelta) -> str:
    encode = {
        "sub": user.email,
        "id": str(user.id),
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
        refresh_token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    payload = decode_refresh_token(refresh_token=refresh_token)
    if not (payload.get("sub") or not payload.get("id")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload")
    return payload


def decode_refresh_token(refresh_token: str) -> dict:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTClaimsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail=f'Refresh token is invalid: {str(e)}')

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Refresh token is invalid: + {str(e)}'
        )
