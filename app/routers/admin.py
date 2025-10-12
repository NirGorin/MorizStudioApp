
from typing import List, Optional

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from .auth import *
from ..schemas import CreateStudioRequest,UserResponse,TraineeProfileUsersMatchResponse
from .trainee_profile import *
from .users import *

def get_redis_optional():
        return None

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users_by_studio/{studio_id}", status_code=status.HTTP_200_OK,response_model=List[UserResponse])
async def get_users_by_studio(
    studio_id: int,
    db: db_dependecy,           
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user.get('role') != "admin" or (user_model.studio_id != studio_id):
        raise HTTPException(status_code=403, detail="User role not allowed to access users by studio")
    users = db.query(User).filter(User.studio_id == studio_id).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for the specified studio")
    return users

@router.get("/trainee_profiles_by_studio/{studio_id}", status_code=status.HTTP_200_OK)
async def get_trainee_profiles_by_studio(
    studio_id: int,
    db: db_dependecy,
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    if (user.get('role') != "admin") or (user_model.studio_id != studio_id):
        raise HTTPException(status_code=403, detail="User role not allowed to access trainee profiles by studio")

    trainee_profiles = (
        db.query(TraineeProfile)
        .join(User, TraineeProfile.user_id == User.id)
        .filter(User.studio_id == studio_id)
        .all()
    )

    if not trainee_profiles:
        raise HTTPException(status_code=404, detail="No trainee profiles found for the specified studio")

    return trainee_profiles


@router.get("/trainees/{profile_id}/profile", status_code=status.HTTP_200_OK)
async def get_trainee_profile_cach_admin_only(
    profile_id: int,
    db: db_dependecy,
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    tp = db.query(TraineeProfile).filter(TraineeProfile.id == profile_id).first()
    if not tp:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    owner_user = db.query(User).filter(User.id == tp.user_id).first()
    if not owner_user:
        raise HTTPException(status_code=404, detail="Trainee profile not associated with any user")

    requester = db.query(User).filter(User.id == user.get("id")).first()
    if not requester or requester.studio_id != owner_user.studio_id:
        raise HTTPException(status_code=403, detail="Admin not allowed: different studio")

    cache_key = f"trainee:{profile_id}:profile"
    try:
        raw = await r.get(cache_key)
    except Exception:
        raw = None

    if raw:
        try:
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode("utf-8", errors="ignore")
            data = json.loads(raw)
        except Exception:
            data = {"raw": raw}
        return {"profile_id": profile_id, "cache": "HIT", "data": data}

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
        "ai_summary": tp.ai_summary,
        "ai_json": tp.ai_json,


    }

    try:
        serializable = jsonable_encoder(payload)
        await r.set(cache_key, json.dumps(serializable), ex=CACHE_TTL_SECONDS)
    except Exception:
        pass

    return {"profile_id": profile_id, "cache": "MISS", "data": payload}

@router.get(
    "/trainee_profiles_users_match/{studio_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[TraineeProfileUsersMatchResponse]
)
async def get_trainee_profiles_and_users(
    studio_id: int,
    db: db_dependecy,
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    if (user.get('role') != "admin") or (user_model.studio_id != studio_id):
        raise HTTPException(status_code=403, detail="User role not allowed to access trainee profiles by studio")

    rows = (
        db.query(TraineeProfile, User)
        .join(User, TraineeProfile.user_id == User.id)
        .filter(User.studio_id == studio_id)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="No trainee profiles found for the specified studio")

    result = [
        TraineeProfileUsersMatchResponse(
            id=u.id,
            first_name=u.first_name,
            last_name=u.last_name,
            username=u.username,
            email=u.email,
            phone_number=u.phone_number,
            role=u.role,
            studio_id=u.studio_id,
            profile_id=tp.id,
            age=tp.age,
            gender=tp.gender,
            height_cm=tp.height_cm,
            weight_kg=tp.weight_kg,
            level=tp.level,
            number_of_week_training=tp.number_of_week_training,
            limitations=tp.limitations,
            ai_status=tp.ai_status,
            ai_summary=tp.ai_summary,
            ai_json=tp.ai_json,
        )
        for (tp, u) in rows
    ]

    return result



@router.delete("/delete_studio/{studio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_studio(
    studio_id: int,
    db: db_dependecy,           
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user.get('role') != "admin" and (user_model.studio_id != studio_id):
        raise HTTPException(status_code=403, detail="Not allowed to delete studio")
    studio = db.query(Studio).filter(Studio.id == studio_id).first()
    if not studio:
        raise HTTPException(status_code=404, detail="Studio not found")
    db.delete(studio)
    db.commit()
    return {"message": "Studio deleted successfully"}

@router.delete("/delete_trainee_profile/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trainee_profile(
    profile_id: int,
    db: db_dependecy,
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    profile = db.query(TraineeProfile).filter(TraineeProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    profile_user = db.query(User).filter(User.id == profile.user_id).first()
    if not profile_user:
        raise HTTPException(status_code=404, detail="Trainee profile not associated with any user")

    requester = db.query(User).filter(User.id == user.get('id')).first()
    if requester is None:
        raise HTTPException(status_code=404, detail="User not found")

    if (user.get('role') != "admin") or (requester.studio_id != profile_user.studio_id):
        raise HTTPException(status_code=403, detail="Not allowed to delete trainee profile")

    db.delete(profile)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: db_dependecy,           
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_admin = db.query(User).filter(User.id == user.get('id')).first()
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get('role') != "admin" and (user_admin.studio_id != user_to_delete.studio_id):
        raise HTTPException(status_code=403, detail="Not allowed to delete user")
    db.delete(user_to_delete)
    db.commit()
    return {"message": "User deleted successfully"}

@router.delete("/delete_user_from_studio/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_from_studio(
    user_id: int,
    db: db_dependecy,           
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_admin = db.query(User).filter(User.id == user.get('id')).first()
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get('role') != "admin" and (user_admin.studio_id != user_to_delete.studio_id):
        raise HTTPException(status_code=403, detail="Not allowed to delete user from studio")
    user_to_delete.studio_id = None
    db.add(user_to_delete)
    db.commit()
    return {"message": "User removed from studio successfully"}

@router.put("/update_studio/{studio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_studio(
    studio_id: int,
    studio_request: CreateStudioRequest,
    db: db_dependecy,           
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user.get('role') != "admin" and (user_model.studio_id != studio_id):
        raise HTTPException(status_code=403, detail="Not allowed to update studio")
    studio = db.query(Studio).filter(Studio.id == studio_id).first()
    if not studio:
        raise HTTPException(status_code=404, detail="Studio not found")
    studio.name = studio_request.Name
    studio.studio_email = studio_request.Email
    db.add(studio)
    db.commit()
    return {"message": "Studio updated successfully"}