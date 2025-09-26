# #routers.admin file:
# from fastapi import APIRouter
# from .auth import *
# from .trainers import *
# from .limitations import *

# router = APIRouter(prefix="/admin", tags=["admin"])

# class TrainerLimitationResponse(BaseModel):
#     Username: Optional[str] = None
#     Limitation: Optional[list] = None

# class AdminLimitationRequest(BaseModel):
#         limitation: str

#         model_config = ConfigDict(from_attributes=True)

# @router.get("/limitations")
# async def get_limitations(user: user_dependecy, db: db_dependecy):
#    if user is None:
#        raise HTTPException(status_code=401, detail="User not authenticated")
#    if user.get('role') != "admin":
#        raise HTTPException(status_code=403, detail="User not allowed")
#    user_model=db.query(Limitation).all()
#    if user_model is None:
#        raise HTTPException(status_code=404, detail="Limitation not found")

#    return user_model

# @router.get("/trainer_limitation",response_model=List[TrainerLimitationResponse])
# async def get_limitations(user: user_dependecy, db: db_dependecy):
#     if user is None:
#         raise HTTPException(status_code=401, detail="User not authenticated")
#     if user.get('role') != "admin":
#         raise HTTPException(status_code=403, detail="User not allowed")
#     trainers=db.query(Trainer).all()
#     response=[]
#     for trainer in trainers:
#         lim_list=[lim.limitation for lim in trainer.Limitations]
#         response.append(TrainerLimitationResponse(Username= trainer.username,
#             Limitation = lim_list))
#     return response


# @router.post("/limitations",status_code=status.HTTP_201_CREATED)
# async def limitations(user: user_dependecy, db: db_dependecy, limitation: AdminLimitationRequest):
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     if user.get('role') != "admin":
#         raise HTTPException(status_code=403, detail="User not allowed")
#     limitation_model = Limitation(limitation=limitation.limitation)
#     db.add(limitation_model)
#     db.commit()

from typing import List
from .auth import *
from ..schemas import CreateStudioRequest,UserResponse
from .trainers import *
from .trainee_profile import *
from .users import *

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
    if user.get('role') != "admin" and (user_model.studio_id != studio_id):
        raise HTTPException(status_code=403, detail="User role not allowed to access users by studio")
    users = db.query(User).filter(User.studio_id == studio_id).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for the specified studio")
    return users

@router.get("/trainee_profiles_by_studio/{studio_id}", status_code=status.HTTP_200_OK, response_model_exclude={"password", "hashed_password"})
async def get_trainee_profiles_by_studio(
    studio_id: int,
    db: db_dependecy,           
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user.get('role') != "admin" and (user_model.studio_id != studio_id):
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

@router.get("/get_trainee_profile/{profile_id}", status_code=status.HTTP_200_OK)
async def get_trainee_profile_by_cache_and_by_db(
    profile_id: int,
    db: db_dependecy,           
    user: user_dependecy
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    trainee_profile_user = db.query(User).filter(User.trainee_id == profile_id).first()
    if not trainee_profile_user:
        raise HTTPException(status_code=404, detail="Trainee profile not associated with any user")
    if user.get('role') != "admin" and (user_model.studio_id != trainee_profile_user.studio_id):
        raise HTTPException(status_code=403, detail="User role not allowed to access this trainee profile")
    
    cache_key = f"trainee:{profile_id}:profile"
    cached_profile = await r.get(cache_key)
    if cached_profile:
        try:
            data = json.loads(cached_profile)
        except json.JSONDecodeError:
            raw = await r.get(cache_key)
            data = {"raw": raw}
        return {"profile_id": profile_id, "cache": "HIT", "data": data}

    
    tp = db.query(TraineeProfile).filter(TraineeProfile.id == profile_id).first()
    if not tp:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    
    payload = {
        "profile_id": tp.id,
        "user_id": tp.user_id,
        "age": tp.age,
        "gender": tp.gender,
        "height_cm": tp.height_cm,
        "weight_kg": tp.weight_kg,
        "level": tp.level,
        "number_of_week_training": tp.number_of_week_training,
        "limitations": tp.limitations,
        "ai_status": tp.ai_status,
        "ai_summary": tp.ai_summary,
        "ai_json": tp.ai_json,
    }
    try:
        await r.setex(cache_key, 3600, json.dumps(payload))
    except Exception:
        pass
    return {"profile_id": profile_id, "cache": "MISS", "data": payload}





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
    user_trainee_profile = db.query(User).filter(User.trainee_id == profile_id).first()
    if not user_trainee_profile:
        raise HTTPException(status_code=404, detail="Trainee profile not associated with any user")
    user_admin = db.query(User).filter(User.id == user.get('id')).first()
    if user.get('role') != "admin" and (user_admin.studio_id != user_trainee_profile.studio_id):
        raise HTTPException(status_code=403, detail="Not allowed to delete trainee profile")
    profile = db.query(TraineeProfile).filter(TraineeProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Trainee profile not found")
    db.delete(profile)
    db.commit()
    return {"message": "Trainee profile deleted successfully"}

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
