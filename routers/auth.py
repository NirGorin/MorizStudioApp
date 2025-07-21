#routers.auth file:
from datetime import timedelta, datetime, UTC
from typing import Annotated

from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sqlalchemy.testing.pickleable import User

from ..database import SessionMoriz
from ..models import Trainer

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
token_jwt = Annotated[str,Depends(oauth2_scheme)]

bcryptcontext=CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db=SessionMoriz()
    try:
        yield db
    finally:
        db.close()

db_dependecy = Annotated[Session,Depends(get_db)]

ALGORITHM = "HS256"
SECRET_KEY='fb1d8bb425809a98950a445e1300c7696f8eaf118724754aeaf96ac0f647dcc9'

class CreateTrainerRequest(BaseModel):
    First_Name : str
    Last_Name : str
    username : str
    Email : str
    Password : str
    Level : str
    Number_Of_Training : int
    Role: str
    Phone_Number : str


class Token(BaseModel):
    access_token: str
    token_type: str

def authenticate_user(username: str, password: str, db: db_dependecy):
    user_model= db.query(Trainer).filter(Trainer.username == username).first()
    if not user_model or not bcryptcontext.verify(password, user_model.Password):
        return False
    return user_model


def create_access_token(username: str,id: int, Role: str, expires_delta: timedelta ):
    to_encode = {"sub": username, "id": id, "role": Role}
    expires_time = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expires_time})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: token_jwt):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        role: str = payload.get('role')
        if not username or not user_id:
            raise HTTPException(status_code=401, detail="Username not found")
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate user")

@router.post("/create_trainer",status_code=status.HTTP_201_CREATED)
async def create_trainer(db: db_dependecy, trainer: CreateTrainerRequest):
    trainer_model=Trainer(
        First_Name=trainer.First_Name,
        Last_Name=trainer.Last_Name,
        username=trainer.username,
        Email=trainer.Email,
        Password=bcryptcontext.hash(trainer.Password),
        Level=trainer.Level,
        Number_Of_Training=trainer.Number_Of_Training,
        Role=trainer.Role,
        Phone_Number=trainer.Phone_Number,
        )
    db.add(trainer_model)
    db.commit()

@router.post("/login",response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependecy):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(user.username, user.ID, user.Role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


