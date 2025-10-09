# trainee_profile.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import json, os
from ..models import TraineeProfile
from ..services.ai_service import process_profile_in_background
from ..schemas import CreateTraineeProfileRequest
from ..routers.auth import get_current_user
from .auth import get_db                
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r: Redis = Redis.from_url(REDIS_URL, decode_responses=True)
CACHE_TTL_SECONDS = 3600

router = APIRouter(prefix="/trainee_profile", tags=["trainee_profile"])

@router.delete("/delete_trainee_profile/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trainee_profile(
    profile_id: int,
    db: Session = Depends(get_db),           
    user: dict = Depends(get_current_user),
):
    if user['role'] == 'trainer':
        raise HTTPException(status_code=403, detail="User role not allowed to delete trainee profile")
    profile = db.query(TraineeProfile).filter(TraineeProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Trainee profile not found")
    db.delete(profile)
    db.commit()
    return {"message": "Trainee profile deleted successfully"}

@router.post("/create_trainee_profile", status_code=status.HTTP_201_CREATED)
async def create_trainee_profile(
    profile: CreateTraineeProfileRequest,    
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),           
    user: dict = Depends(get_current_user),
):
    if user['role'] == 'trainer':
        raise HTTPException(status_code=403, detail="User role not allowed to create trainee profile")

    trainee_profile = TraineeProfile(
        age=profile.Age,
        gender=profile.Gender,
        height_cm=profile.Height,
        weight_kg=profile.Weight,
        level=profile.Level,
        number_of_week_training=profile.Number_Of_Week_Training,
        limitations=profile.Limitation,
        user_id=user['id'],
        ai_status="queued",
    )
    db.add(trainee_profile)
    db.commit()
    db.refresh(trainee_profile)

    cache_key = f"trainee:{trainee_profile.id}:profile"
    cache_payload = {
        "profile_id": trainee_profile.id,
        "user_id": user["id"],
        "age": profile.Age,
        "gender": profile.Gender,
        "height_cm": profile.Height,
        "weight_kg": profile.Weight,
        "level": profile.Level,
        "number_of_week_training": profile.Number_Of_Week_Training,
        "limitations": profile.Limitation,
        "ai_status": "queued",
    }
    try:
        await r.set(cache_key, json.dumps(cache_payload), ex=CACHE_TTL_SECONDS)
    except Exception:
        pass

    background_tasks.add_task(process_profile_in_background, trainee_profile.id)
    return {"message": "Trainee profile created successfully", "profile_id": trainee_profile.id}

@router.get("/trainees/{profile_id}/profile_cache", status_code=status.HTTP_200_OK)
async def get_trainee_profile_cache_only(profile_id: int):
    cache_key = f"trainee:{profile_id}:profile"
    try:
        raw = await r.get(cache_key)
    except Exception:
        raise HTTPException(status_code=503, detail="Cache unavailable")
    if not raw:
        raise HTTPException(status_code=404, detail="Cache miss for trainee profile")
    try:
        data = json.loads(raw)
    except Exception:
        data = {"raw": raw}
    return {"profile_id": profile_id, "cache": "HIT", "data": data}

@router.get("/trainees/{profile_id}/profile", status_code=status.HTTP_200_OK)
async def get_trainee_profile(
    profile_id: int,
    db: Session = Depends(get_db),           
):
    cache_key = f"trainee:{profile_id}:profile"
    try:
        raw = await r.get(cache_key)
    except Exception:
        raw = None
    if raw:
        try:
            data = json.loads(raw)
        except Exception:
            data = {"raw": raw}
        return {"profile_id": profile_id, "cache": "HIT", "data": data}

    tp = db.query(TraineeProfile).filter(TraineeProfile.id == profile_id).first()
    if not tp:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    payload = {
        "profile_id": tp.id,
        "user_id": tp.user_id,
        "age": tp.age,
        "gender": getattr(tp.gender, "name", tp.gender),
        "height_cm": tp.height_cm,
        "weight_kg": tp.weight_kg,
        "level": getattr(tp.level, "name", tp.level),
        "number_of_week_training": tp.number_of_week_training,
        "limitations": tp.limitations,
        "ai_status": tp.ai_status,
    }
    try:
        await r.set(cache_key, json.dumps(payload), ex=CACHE_TTL_SECONDS)
    except Exception:
        pass
    return {"profile_id": profile_id, "cache": "MISS", "data": payload}

@router.put("/update_trainee_profile/{profile_id}", status_code=status.HTTP_200_OK)
async def update_trainee_profile(
    profile_id: int,
    profile: CreateTraineeProfileRequest,    
    db: Session = Depends(get_db),           
    user: dict = Depends(get_current_user),
):
    if user['role'] == 'trainer':
        raise HTTPException(status_code=403, detail="User role not allowed to update trainee profile")
    profile_model = db.query(TraineeProfile).filter(TraineeProfile.id == profile_id).first()
    if not profile_model:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    profile_model.age = profile.Age
    profile_model.gender = profile.Gender
    profile_model.height_cm = profile.Height
    profile_model.weight_kg = profile.Weight
    profile_model.level = profile.Level
    profile_model.number_of_week_training = profile.Number_Of_Week_Training
    profile_model.limitations = profile.Limitation

    db.add(profile_model)
    db.commit()
    db.refresh(profile_model)
    cache_key = f"trainee:{profile_model.id}:profile"
    cache_payload = {
        "profile_id": profile_model.id,
        "user_id": profile_model.user_id,
        "age": profile_model.age,
        "gender": profile_model.gender,
        "height_cm": profile_model.height_cm,
        "weight_kg": profile_model.weight_kg,
        "level": profile_model.level,
        "number_of_week_training": profile_model.number_of_week_training,
        "limitations": profile_model.limitations,
        "ai_status": profile_model.ai_status,
    }
    try:
        await r.set(cache_key, json.dumps(cache_payload), ex=CACHE_TTL_SECONDS)
    except Exception:
        pass
    return {"message": "Trainee profile updated successfully", "profile_id": profile_model.id}
    
