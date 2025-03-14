from fastapi import APIRouter, status, HTTPException
from passlib.context import CryptContext
from sqlalchemy import select

from database import db_dependency
from models.user_model import User
from schemas.user_request_schema import UserRequestSchema, UserResponseSchema

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/v1/authentication", tags=["auth"])


@router.post("/registration", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def registration(db: db_dependency, request: UserRequestSchema):
    user_data = request.model_dump()
    result = await db.execute(select(User).where(User.email == user_data["email"]))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with such email already exists")
    user_data['hashed_password'] = bcrypt_context.encrypt(user_data['password'])
    user_data.pop('password', None)
    user_object = User(**user_data)
    db.add(user_object)
    await db.commit()
    await db.refresh(user_object)
    return user_object
