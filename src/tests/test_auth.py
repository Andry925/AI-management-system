import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from models.user_model import User
from routers.auth import authenticate_user
from utils.authentication_utils import decode_refresh_token
from .utils import TestingSession, async_client, create_user,create_test_db

USER_DATA = {
    "username": "johndoe1234",
    "email": "rega600b@gmail.com",
    "password": "Panel@2004",
}


@pytest.mark.asyncio
async def test_authenticate_user(create_user):
    async with TestingSession() as db:
        authenticated_user = await authenticate_user(db=db, email=create_user.email, password="Panel@2004")
        assert authenticated_user is not None
        assert authenticated_user.email == create_user.email
        assert authenticated_user.username == create_user.username


@pytest.mark.asyncio
async def test_authenticate_user_invalid_user(create_user):
    async with TestingSession() as db:
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(db, email=create_user.email, password="Panel@2003")
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == 'Incorrect password provided'


@pytest.mark.asyncio
async def test_register_user(create_user, async_client):
    response = await async_client.post('api/v1/authentication/registration', json=USER_DATA)
    assert response.status_code == 201
    async with TestingSession() as db:
        result = await db.execute(select(User).filter_by(email=USER_DATA['email']))
        created_user = result.scalars().first()
    assert created_user is not None


@pytest.mark.asyncio
async def test_authenticate_user_already_registered(create_user, async_client):
    REGISTERED_USER_DATA = {
        "email": create_user.email,
        "password": "Panel@2004",
        "username": create_user.username
    }
    response = await async_client.post('/api/v1/authentication/registration', json=REGISTERED_USER_DATA)
    assert response.status_code == 400
    assert response.json()["detail"] == 'User with such email already exists'


@pytest.mark.asyncio
async def test_login_user(create_user, async_client):
    await async_client.post('api/v1/authentication/registration', json=USER_DATA)
    response = await async_client.post('api/v1/authentication/login', json=USER_DATA)
    access_token = response.json().get('access_token')
    payload = decode_refresh_token(access_token)
    assert response.status_code == 200
    assert access_token is not None
    assert payload.get('sub') == USER_DATA.get('email')



