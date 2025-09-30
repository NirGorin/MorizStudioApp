#main file:
from fastapi import FastAPI
import os
from app.database import engine, Base
from app.routers import  auth,users,trainee_profile,studios,admin

app=FastAPI()

@app.get("/healthz")
def healthz():
    return {"ok": True}

if os.getenv("RUN_SYNC_DB") == "true":
    Base.metadata.create_all(bind=engine)





app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(trainee_profile.router)
app.include_router(studios.router)
