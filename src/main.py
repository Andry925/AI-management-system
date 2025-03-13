from fastapi import FastAPI


app = FastAPI()


@app.get("/healthy")
async def healthy():
    return {"healthy": True}