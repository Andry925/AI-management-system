from fastapi import FastAPI

from database import init_db
from routers import auth, notes
from models.user_model import User
from models.notes_model import Note

app = FastAPI()


@app.get("/healthy")
async def healthy():
    return {"healthy": True}


@app.on_event("startup")
async def on_startup():
    await init_db()


app.include_router(auth.router)
app.include_router(notes.router)
