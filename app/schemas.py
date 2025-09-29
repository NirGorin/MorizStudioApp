from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict
from typing import Optional






class CreateUserRequest(BaseModel):
    First_Name : str
    Last_Name : str
    Username : str
    Email : str
    Password : str
    Role: str
    Phone_Number: str

class CreateTraineeProfileRequest(BaseModel):
    Age: int
    Gender: str
    Height: int
    Weight: int
    Level: str
    Number_Of_Week_Training: str
    Limitation: str = None

class CreateStudioRequest(BaseModel):
    Name: str
    Email: str

class UpdatePasswordRequest(BaseModel):
    Password: str
    Newpassword: str

class updateUsernameRequest(BaseModel):
    Username: str
    Newusername: str
    


class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str  
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str  
    studio_id: Optional[int] = None
    phone_number: Optional[str] = None
    trainee_id: Optional[int] = None

    

   
    model_config = ConfigDict(from_attributes=True)

class TraineeProfileUsersMatchResponse(BaseModel):
    id: int
    username: str  
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str  
    studio_id: Optional[int] = None
    phone_number: Optional[str] = None
    trainee_id: Optional[int] = None
    profile_id: int
    age: int
    gender: str
    height_cm: int
    weight_kg: int
    level: str
    number_of_week_training: int
    limitations: Optional[str] = None
    ai_status: str
    ai_summary: Optional[str] = None
    ai_json: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)