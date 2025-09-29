# app/routers/studios.py
import re
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from ..models import Studio, User
from ..schemas import CreateStudioRequest
from ..services.events import publish_event
from .auth import get_current_user,db_dependecy
from .users import user_dependecy

router = APIRouter(prefix="/studios", tags=["studios"])

def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "studio"

@router.post("/create_studio", status_code=status.HTTP_201_CREATED)
async def create_studio(
    db: db_dependecy,
    studio: CreateStudioRequest,
    user: user_dependecy,
):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="User role not allowed to create studio")

    studio_model = Studio(name=studio.Name, studio_email=studio.Email)
    db.add(studio_model)
    db.commit()
    db.refresh(studio_model)

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    user_model.studio_id = studio_model.id
    db.add(user_model)
    db.commit()

    publish_event(
        "studio.created",
        {
            "studio_id": studio_model.id,
            "studio_name": studio_model.name,
            "studio_slug": _slugify(studio_model.name),
            "studio_email": studio_model.studio_email,
            "owner_user_id": user_model.id,
        },
    )

    return {
        "message": "Studio created successfully",
        "studio_id": studio_model.id
    }

@router.get("/{studio_id}/", status_code=status.HTTP_200_OK)
async def get_all_studios(db: db_dependecy):
    studios = db.query(Studio).all()
    return studios


@router.post("/registering_to_studio", status_code=status.HTTP_201_CREATED)
async def register_studio(
    db: db_dependecy,
    studio_name: str,
    user: user_dependecy
):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_model.studio_id:
        raise HTTPException(status_code=400, detail="User already registered to a studio")

    existing_studio = db.query(Studio).filter(Studio.name == studio_name).first()
    if not existing_studio:
        raise HTTPException(status_code=404, detail="Studio not found")

    user_model.studio_id = existing_studio.id
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    publish_event(
        "trainee.registered",
        {
            "studio_id": existing_studio.id,
            "studio_name": existing_studio.name,
            "trainee_user_id": user_model.id,
            "trainee_email": getattr(user_model, "email", None),
        },
    )

    return {"message": "User registered to studio successfully", "studio_id": existing_studio.id}