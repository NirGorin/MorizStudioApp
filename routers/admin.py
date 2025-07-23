#routers.admin file:
from fastapi import APIRouter
from .auth import *
from .trainers import *
from .limitations import *

router = APIRouter(prefix="/admin", tags=["admin"])

class TrainerLimitationResponse(BaseModel):
    Username: Optional[str] = None
    Limitation: Optional[list] = None

class AdminLimitationRequest(BaseModel):
        limitation: str

        model_config = ConfigDict(from_attributes=True)

@router.get("/limitations")
async def get_limitations(user: user_dependecy, db: db_dependecy):
   if user is None:
       raise HTTPException(status_code=401, detail="User not authenticated")
   if user.get('role') != "admin":
       raise HTTPException(status_code=403, detail="User not allowed")
   user_model=db.query(Limitation).all()
   if user_model is None:
       raise HTTPException(status_code=404, detail="Limitation not found")

   return user_model

@router.get("/trainer_limitation",response_model=List[TrainerLimitationResponse])
async def get_limitations(user: user_dependecy, db: db_dependecy):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    if user.get('role') != "admin":
        raise HTTPException(status_code=403, detail="User not allowed")
    trainers=db.query(Trainer).all()
    response=[]
    for trainer in trainers:
        lim_list=[lim.limitation for lim in trainer.Limitations]
        response.append(TrainerLimitationResponse(Username= trainer.username,
            Limitation = lim_list))
    return response


@router.post("/limitations",status_code=status.HTTP_201_CREATED)
async def limitations(user: user_dependecy, db: db_dependecy, limitation: AdminLimitationRequest):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get('role') != "admin":
        raise HTTPException(status_code=403, detail="User not allowed")
    limitation_model = Limitation(limitation=limitation.limitation)
    db.add(limitation_model)
    db.commit()


