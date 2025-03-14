from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy import select

from database import db_dependency
from models.user_model import User
from schemas.user_request_schema import UserRequestSchema, UserResponseSchema, LoginRequestSchema
from utils.authentication_utils import authenticate_user, create_jwt_token, get_current_user

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


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(db: db_dependency, request: LoginRequestSchema):
    login_request = request.model_dump()
    email = login_request.get("email")
    password = login_request.get("password")
    user = await authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    access_token = create_jwt_token(user, expires_delta=timedelta(minutes=30))
    response = JSONResponse({"access_token": access_token})
    return response


user_dependency = Annotated[dict, Depends(get_current_user)]
