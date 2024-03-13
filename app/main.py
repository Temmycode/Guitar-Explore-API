from fastapi import FastAPI
from . import models
from .database import engine
from .routers import users, auth

app = FastAPI()


@app.get("/")
def root():
    return {"data": "Hello world"}


app.include_router(users.router)

app.include_router(auth.router)
