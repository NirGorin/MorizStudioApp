#routers.limitations file:
from fastapi import APIRouter
from pydantic import ConfigDict

from . import trainers
from .auth import *
from .trainers import *
from ..models import *

router = APIRouter(prefix="/limitations", tags=["limitations"])


class LimitationRequest(BaseModel):
    username: str
    limitation: str

    model_config = ConfigDict(from_attributes=True)



@router.post("/trainer_limitation",status_code=status.HTTP_201_CREATED)
async def create_trainer_limitations(user: user_dependecy,request: LimitationRequest, db: db_dependecy):
    if user is None:
        raise HTTPException(status_code=401, detail="User validate")
    trainer=db.query(Trainer).filter(Trainer.username==request.username).first()
    if trainer is None:
        raise HTTPException(status_code=404, detail="User not found")
    limitation_model=db.query(Limitation).filter(Limitation.limitation==request.limitation).first()
    if limitation_model is None :
        raise HTTPException(status_code=404, detail="No such limitation")
    trainer.Limitations.append(limitation_model)
    db.commit()

# @router.put("/",status_code=status.HTTP_204_NO_CONTENT)
# async def update_trainer_limitations(user: user_dependecy,trainer_request: UserLimitationRequest,limitation_request: LimitationRequest,
#                                      db: db_dependecy):
#     if user is None:
#         raise HTTPException(status_code=401, detail="User not validate")
#     trainer_model=db.query(Trainer).filter(Trainer.ID==user.get('id')).first()
#     if trainer_model is None:
#         raise HTTPException(status_code=404, detail="No such trainer")
#     trainer=Trainer(username=trainer_request.username)
#     if trainer is None:
#         raise HTTPException(status_code=404, detail="User not change")
#     db.add(trainer)
#     db.commit()
#     limitation_model=db.query(Limitation).filter(Limitation.limitation==limitation_request.limitation).first()
#     if limitation_model is None :
#         raise HTTPException(status_code=404, detail="No such limitation")
#     limitation=Limitation(limitation=limitation_request.limitation)
#     db.add(limitation_model)
#     db.commit()








