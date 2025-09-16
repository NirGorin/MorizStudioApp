#main file:
from fastapi import FastAPI

from .database import engine, Base
from .routers import trainers, auth, limitations, admin,users,trainee_profile,studios

app=FastAPI()
Base.metadata.create_all(bind=engine)


app.include_router(trainers.router)
app.include_router(auth.router)
app.include_router(limitations.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(trainee_profile.router)
app.include_router(studios.router)