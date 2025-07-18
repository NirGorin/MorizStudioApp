#main file:
from fastapi import FastAPI

from MorizApp.database import engine, Base
from MorizApp.routers import trainers, auth, limitations, admin

app=FastAPI()
Base.metadata.create_all(bind=engine)


app.include_router(trainers.router)
app.include_router(auth.router)
app.include_router(limitations.router)
app.include_router(admin.router)