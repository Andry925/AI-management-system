from fastapi import FastAPI

from database import init_db
from routers import auth

app = FastAPI()


@app.get("/healthy")
async def healthy():
    return {"healthy": True}


@app.on_event("startup")
async def on_startup():
    await init_db()


app.include_router(auth.router)
