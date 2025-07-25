#test.test_trainers file:
from MorizApp.routers.auth import get_current_user
from MorizApp.routers.trainers import get_db

from fastapi import status

from MorizApp.test.utils import override_get_current_user,override_get_db

from .utils import *

app.dependency_overrides[get_current_user]=override_get_current_user
app.dependency_overrides[get_db]=override_get_db

def test_get_trainers(test_Trainer):
    response=client.get('/Trainers')
    assert response.status_code==status.HTTP_200_OK
    assert response.json() == [{
        "First_Name": "Mor",
        "Last_Name": "Gorin",
        "Email": "morbara2@gmail.com",
        "Level": "Professional",
        "Number_Of_Training": 0,
        "Role": "admin",
        "Phone_Number": "+972 50-838-9904"
    }]

def test_post_trainers(test_Trainer):
    trainer= {"First_Name": "Mor",
        "Last_Name": "Gorin",
        "username": "Morizz",
        "Email": "mmorbara2@gmail.com",
        "Password": "test1234",
        "Level": "Professional",
        "Number_Of_Training": 0,
        "Role": "admin",
        "Phone_Number": "972 50-838-9904"}
    response=client.post('/auth/create_trainer', json=trainer)
    assert response.status_code==status.HTTP_201_CREATED
    db=TestingSession()
    user_model =db.query(Trainer).filter(Trainer.ID==2).first()
    assert user_model is not None
    assert user_model.ID==2
    assert user_model.First_Name=="Mor"
    assert user_model.Last_Name=="Gorin"
    assert user_model.Level=="Professional"
    assert user_model.Number_Of_Training==0
    assert user_model.Role=="admin"

def test_update_trainers(test_Trainer):
    request_trainer = {
        "First_Name": "Mor",
        "Last_Name": "Gorin",
        "Email": "morbara2@gmail.com",
        "Level": "Master",
        "Number_Of_Training": 0,
        "Role": "admin",
        "Phone_Number": "+972 50-838-9904"
    }

    response=client.put('/Trainers',json=request_trainer)
    assert response.status_code==status.HTTP_204_NO_CONTENT
    db=TestingSession()
    trainer_model=db.query(Trainer).filter(Trainer.ID==test_Trainer.ID).first()
    print(trainer_model)
    assert trainer_model.Level=="Master"

def test_not_update_trainers(test_Trainer):
    request_trainer = {
        "First_Name": "Mor",
        "Last_Name": "Gorin",
        "Email": "morbara2@gmail.com",
        "Level": "Master",
        "Number_Of_Training": 0,
        "Role": "admin",
        "Phone_Number": "+972 50-838-9904"
    }

    response=client.put('/Trainers',json=request_trainer)
    assert response.status_code==status.HTTP_204_NO_CONTENT
    db=TestingSession()
    trainer_model=db.query(Trainer).filter(Trainer.ID==test_Trainer.ID).first()
    assert trainer_model.Level!="Professional"