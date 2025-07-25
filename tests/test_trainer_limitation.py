#test.test_trainer_limitation file:
from .utils import *
from fastapi import status
from MorizApp.routers.auth import get_current_user,get_db


app.dependency_overrides[get_current_user]=override_get_current_user
app.dependency_overrides[get_db]=override_get_db

def test_create_trainer_limitations(test_data):
    payload = {
        "username": "Moriz",
        "limitation": "Pregnancy"
    }
    response=client.post("/limitations/trainer_limitation",json=payload)
    assert response.status_code==status.HTTP_201_CREATED
    db=TestingSession()
    trainer_model=db.query(Trainer).filter(Trainer.username==payload["username"]).first()
    result=db.execute(text("SELECT * FROM trainer_limitation;")).fetchone()
    assert result is not None
    assert result == (1,1)
    assert trainer_model.Limitations[0].limitation == 'Pregnancy'

    db = TestingSession()
    db.execute(text("DELETE FROM trainer_limitation;"))
    db.execute(text("DELETE FROM limitations;"))
    db.execute(text("DELETE FROM trainers;"))
    db.commit()

