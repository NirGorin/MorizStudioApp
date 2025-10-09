# app/routers/users.py
import os
import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import CreateUserRequest
from .auth import get_db
from ..models import User  

router = APIRouter(prefix="/users", tags=["users"])


r = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)



REDIS_URL = os.getenv("REDIS_URL")


r = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)

CACHE_TTL_SECONDS = 600

@router.get("/{user_id}/",status_code=200)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(User).filter(User.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    return user_model

@router.get("/{user_id}/email")
def get_user_email(user_id: int, db: Session = Depends(get_db)):
    key = f"user:{user_id}:email"

    
    email = r.get(key)
    if email:
        return {"user_id": user_id, "email": email, "cache": "HIT"}

    
    email = db.query(User.email).filter(User.id == user_id).scalar()
    if email is None:
        raise HTTPException(status_code=404, detail="User not found")

    
    r.setex(key, CACHE_TTL_SECONDS, email)

    
    return {"user_id": user_id, "email": email, "cache": "MISS"}

@router.delete("/{user_id}/")
def delete_user_email(username: str, db: Session = Depends(get_db)):
    user_model = db.query(User).filter(User.username == username).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_model)
    db.commit()
    return {"message": "User deleted successfully"}


@router.put("/{user_id}/update_user")
def update_user(user_id: int, user: CreateUserRequest, db: Session = Depends(get_db)):
    user_model = db.query(User).filter(User.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.first_name = user.First_Name
    user_model.last_name = user.Last_Name
    user_model.email = user.Email
    user_model.phone_number = user.Phone_Number
    db.commit()
    db.refresh(user_model)
    
    
    key = f"user:{user_id}:email"
    if r.exists(key):
        r.setex(key, CACHE_TTL_SECONDS, user.Email)

    return {"message": "User updated successfully", "user": user_model} 