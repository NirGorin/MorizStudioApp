#tests.utils file:
import pytest
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker, relationship
from starlette.testclient import TestClient

from ..database import Base
from ..main import app
from ..models import Trainer, Limitation
from ..routers.auth import bcryptcontext

client= TestClient(app)

SQLALCHEMY_DATABASE_URL='sqlite:///./testdb.db'
engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread":False},poolclass=StaticPool)

TestingSession=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db=TestingSession()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'sub': 'Moriz', 'id': 1, 'role': 'admin'}

@pytest.fixture(scope='module')
def test_Trainer():
    trainer = Trainer(ID=1,
    First_Name='Mor',
    Last_Name='Gorin',
    username='Moriz',
    Email='morbara2@gmail.com',
    Password=bcryptcontext.hash('test1234'),
    Level='Professional',
    Number_Of_Training=0,
    Role='admin',
    Phone_Number='+972 50-838-9904',
                      )
    db=TestingSession()
    db.add(trainer)
    db.commit()
    yield trainer

    with engine.connect() as connection:
        connection.execute(text("delete from trainers;"))
        connection.commit()

@pytest.fixture(scope='module')
def test_Limitation():
    limitation = Limitation(ID=1,
                            limitation="Pregnancy",
                           )
    db = TestingSession()
    db.add(limitation)
    db.commit()
    yield limitation

    with engine.connect() as connection:
        connection.execute(text("delete from limitations;"))
        connection.commit()


@pytest.fixture(scope='module')
def test_data():
    db = TestingSession()

    # יצירת מגבלה
    limitation = Limitation(ID=1, limitation="Pregnancy")

    # יצירת מאמן עם המגבלה
    trainer = Trainer(
        ID=1,
        First_Name='Mor',
        Last_Name='Gorin',
        username='Moriz',
        Email='morbara2@gmail.com',
        Password=bcryptcontext.hash('test1234'),
        Level='Professional',
        Number_Of_Training=0,
        Role='admin',
        Phone_Number='+972 50-838-9904',
        Limitations=[limitation]  # ← כאן הקישור!
    )

    db.add(trainer)
    db.commit()
    yield trainer

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM trainer_limitation;"))
        connection.execute(text("DELETE FROM trainers;"))
        connection.execute(text("DELETE FROM limitations;"))
        connection.commit()