# app/routers/users.py
import os
from typing import Annotated, List
import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.schemas import CreateUserRequest, UpdatePasswordRequest, updateUsernameRequest,UserResponse,UpdateUserRequest
from .auth import get_db, get_current_user, db_dependecy, bcryptcontext
from ..models import User  

router = APIRouter(prefix="/users", tags=["users"])
user_dependecy = Annotated[dict,Depends(get_current_user)]


r = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)



REDIS_URL = os.getenv("REDIS_URL")


r = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)

CACHE_TTL_SECONDS = 600

@router.get("/{user_id}/",status_code=200,response_model=UserResponse)
def get_user(user_id: int, db: db_dependecy,user: user_dependecy):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized to access user information")
    user_model = db.query(User).filter(User.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's information")
    return user_model

@router.get("/{user_id}/email")
def get_user_email(user_id: int, db: db_dependecy, user: user_dependecy):
    
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized to access user email")
    
    key = f"user:{user_id}:email"

    
    email = r.get(key)
    if email:
        return {"user_id": user_id, "email": email, "cache": "HIT"}

    
    email = db.query(User.email).filter(User.id == user_id).scalar()
    if email is None:
        raise HTTPException(status_code=404, detail="User not found")

    
    r.setex(key, CACHE_TTL_SECONDS, email)

    
    return {"user_id": user_id, "email": email, "cache": "MISS"}

@router.delete("/{username}/")
def delete_user_by_username(username: str, db: db_dependecy, user: user_dependecy):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized to delete user")
    user_model = db.query(User).filter(User.username == username).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    if user_model.id != user.get('id'):
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    db.delete(user_model)
    db.commit()
    return {"message": "User deleted successfully"}


@router.put("/{user_id}/update_user")
def update_user(user_id: int, user: UpdateUserRequest, db: db_dependecy, user_check: user_dependecy):
    if  not user_check:
        raise HTTPException(status_code=403, detail="Not authorized to update user")
    user_model = db.query(User).filter(User.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.first_name = user.First_Name
    user_model.last_name = user.Last_Name
    user_model.email = user.Email
    user_model.phone_number = user.Phone_Number
    user_model.role=user.Role
    db.commit()
    db.refresh(user_model)
    
    
    key = f"user:{user_id}:email"
    if r.exists(key):
        r.setex(key, CACHE_TTL_SECONDS, user.Email)

    return {"message": "User updated successfully", "user": user_model} 

  

@router.put("/{user_id}/update_password")
def update_password(
    user_id: int,
    db: db_dependecy,
    user: user_dependecy,
    password_request: UpdatePasswordRequest
):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized to update password")
    user_model = db.query(User).filter(User.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    if user_model.id != user.get('id'):
        raise HTTPException(status_code=403, detail="Not authorized to update this user's password")
    if not bcryptcontext.verify(password_request.Password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user_model.hashed_password = bcryptcontext.hash(password_request.Newpassword)
    db.commit()
    return {"message": "Password updated successfully"}

@router.put("/{user_id}/update_username")
def update_username(
    user_id: int,
    db: db_dependecy,
    user: user_dependecy,
    username_request: updateUsernameRequest
):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized to update username")
    user_model = db.query(User).filter(User.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    if user_model.id != user.get('id'):
        raise HTTPException(status_code=403, detail="Not authorized to update this user's username")
    existing_user = db.query(User).filter(User.username == username_request.Newusername).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    user_model.username = username_request.Newusername
    db.commit()
    return {"message": "Username updated successfully"}