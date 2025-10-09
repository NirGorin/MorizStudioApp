#routers.trainers file:
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user
from starlette import status
from passlib.context import CryptContext
from ..database import SessionMoriz
from ..models import Trainer

from .auth import get_current_user


router=APIRouter(prefix="/Trainers", tags=["Trainers"])

class TrainersRequest(BaseModel):
    First_Name : str
    Last_Name : str
    Email : Optional[str]=None
    Level : Optional[str]=None
    Number_Of_Training : Optional[int]=None
    Role: Optional[str]=None
    Phone_Number : Optional[str]=None

    model_config = ConfigDict(from_attributes=True)

class NewPassword(BaseModel):
    Password: str
    Newpassword: str

class NewUsername(BaseModel):
    Username: str
    Newusername: str


def get_db():
    db=SessionMoriz()
    try:
        yield db
    finally:
        db.close()



db_dependecy = Annotated[Session,Depends(get_db)]
# trainer_dependecy= Annotated[dict,Depends(Create_Request)]
bcryptcontext=CryptContext(schemes=["bcrypt"], deprecated="auto")
user_dependecy = Annotated[dict,Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK,response_model=List[TrainersRequest])
async def get_all_trainers(user: user_dependecy, db: db_dependecy):
    trainer_model = db.query(Trainer).filter(Trainer.ID==user.get('id')).all()
    if not trainer_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No trainer found")
    return trainer_model

@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_trainer(user: user_dependecy, user_request: TrainersRequest, db: db_dependecy):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_model = db.query(Trainer).filter(Trainer.ID==user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No trainer found")
    user_model.First_Name = user_request.First_Name
    user_model.Last_Name = user_request.Last_Name
    user_model.Email = user_request.Email
    user_model.Level = user_request.Level
    user_model.Number_Of_Training = user_request.Number_Of_Training
    user_model.Role = user_request.Role
    user_model.Phone_Number = user_request.Phone_Number
    db.add(user_model)
    db.commit()

