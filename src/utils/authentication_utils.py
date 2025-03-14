from decouple import config
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from starlette import status

from models.user_model import User

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = "HS256"


async def authenticate_user(db, email: str, password) -> User | bool:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password proviced")
    return user
