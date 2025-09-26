# #tests.utils file:
# import pytest
# from sqlalchemy import create_engine, StaticPool, text
# from sqlalchemy.orm import sessionmaker, relationship
# from starlette.testclient import TestClient

# from ..database import Base
# from ..main import app
# from ..models import Trainer, Limitation
# from ..routers.auth import bcryptcontext

# client= TestClient(app)

# SQLALCHEMY_DATABASE_URL='sqlite:///./testdb.db'
# engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread":False},poolclass=StaticPool)

# TestingSession=sessionmaker(autocommit=False,autoflush=False,bind=engine)
# Base.metadata.create_all(bind=engine)

# def override_get_db():
#     db=TestingSession()
#     try:
#         yield db
#     finally:
#         db.close()

# def override_get_current_user():
#     return {'username': 'Moriz', 'id': 1, 'role': 'admin'}

# @pytest.fixture(scope='module')
# def test_Trainer():
#     trainer = Trainer(ID=1,
#     First_Name='Mor',
#     Last_Name='Gorin',
#     username='Moriz',
#     Email='morbara2@gmail.com',
#     Password=bcryptcontext.hash('test1234'),
#     Level='Professional',
#     Number_Of_Training=0,
#     Role='admin',
#     Phone_Number='+972 50-838-9904',
#                       )
#     db=TestingSession()
#     db.add(trainer)
#     db.commit()
#     yield trainer

#     with engine.connect() as connection:
#         connection.execute(text("delete from trainers;"))
#         connection.commit()

# @pytest.fixture(scope='module')
# def test_Limitation():
#     limitation = Limitation(ID=1,
#                             limitation="Pregnancy",
#                            )
#     db = TestingSession()
#     db.add(limitation)
#     db.commit()
#     yield limitation

#     with engine.connect() as connection:
#         connection.execute(text("delete from limitations;"))
#         connection.commit()


# @pytest.fixture(scope='module')
# def test_data():
#     db = TestingSession()

#     # יצירת מגבלה
#     limitation = Limitation(ID=1, limitation="Pregnancy")

#     # יצירת מאמן עם המגבלה
#     trainer = Trainer(
#         ID=1,
#         First_Name='Mor',
#         Last_Name='Gorin',
#         username='Moriz',
#         Email='morbara2@gmail.com',
#         Password=bcryptcontext.hash('test1234'),
#         Level='Professional',
#         Number_Of_Training=0,
#         Role='admin',
#         Phone_Number='+972 50-838-9904',
#         Limitations=[limitation]  # ← כאן הקישור!
#     )

#     db.add(trainer)
#     db.commit()
#     yield trainer

#     with engine.connect() as connection:
#         connection.execute(text("DELETE FROM trainer_limitation;"))
#         connection.execute(text("DELETE FROM trainers;"))
#         connection.execute(text("DELETE FROM limitations;"))
#         connection.commit()


# # tests/utils.py
# import os

# # נוודא שיש env לטסטים בלבד (לא משפיע על הפרוד/דב שלך)
# os.environ.setdefault("TEST_DATABASE_URL", "sqlite:///./testdb.db")
# os.environ.setdefault("TEST_REDIS_URL", "redis://localhost:6379/0")

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool
# from starlette.testclient import TestClient

# # תמיכה בשני מבני פרויקט (עם/בלי חבילה app)
# try:
#     from ..database import Base
#     from ..main import app
#     from ..routers.auth import get_db as auth_get_db
#     from ..models import User
# except ImportError:
#     from database import Base
#     from main import app
#     from routers.auth import get_db as auth_get_db
#     from models import User

# TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

# # Engine ל-SQLite (קובץ) לטסטים; לא נוגע ב-Postgres שלך
# engine = create_engine(
#     TEST_DATABASE_URL,
#     connect_args={"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {},
#     poolclass=StaticPool if TEST_DATABASE_URL.startswith("sqlite") else None,
# )

# TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base.metadata.create_all(bind=engine)

# # override ל-get_db כדי שכל ה-API יעבוד על DB הטסטים
# def override_get_db():
#     db = TestingSession()
#     try:
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[auth_get_db] = override_get_db

# # לקוח בדיקות אחד שיחיה לכל הטסטים
# client = TestClient(app)

# # עוזר קטן לזריעת משתמשים
# def seed_user(db, **fields):
#     # מוחק לפי id/username אם כבר קיים כדי להימנע מכפילויות
#     if "id" in fields:
#         db.query(User).filter(User.id == fields["id"]).delete()
#     if "username" in fields:
#         db.query(User).filter(User.username == fields["username"]).delete()
#     db.commit()
#     u = User(**fields)
#     db.add(u)
#     db.commit()
#     db.refresh(u)
#     return u

# # tests/utils.py
# import os
# import sys
# from pathlib import Path

# # --- 1) ENV לטסטים בשמות שביקשת ---
# os.environ.setdefault("test_database_url", "sqlite:///./testdb.db")
# os.environ.setdefault("test_redis_url",   "redis://localhost:6379/0")

# # נמפה ל-ENV שהאפליקציה משתמשת בהם בזמן import:
# os.environ.setdefault("DATABASE_URL", os.environ["test_database_url"])
# os.environ.setdefault("REDIS_URL",    os.environ["test_redis_url"])

# # --- 2) לדאוג שהשורש של הפרויקט ב-sys.path לפני import-ים של main/database/models
# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool
# from starlette.testclient import TestClient

# # תמיכה בשני מבני פרויקט (עם/בלי app/)
# try:
#     from ..database import Base
#     from ..main import app
#     from ..routers.auth import get_db as auth_get_db
#     from ..models import User
# except ImportError:
#     from database import Base
#     from main import app
#     from routers.auth import get_db as auth_get_db
#     from models import User

# DATABASE_URL = os.environ["DATABASE_URL"]

# # --- 3) Engine לטסטים (SQLite). לא נוגע ב-Postgres שלך.
# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
#     poolclass=StaticPool if DATABASE_URL.startswith("sqlite") else None,
# )
# TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base.metadata.create_all(bind=engine)

# # --- 4) override ל-get_db כדי שכל הראוטרים ירוצו מול DB הטסטים
# def override_get_db():
#     db = TestingSession()
#     try:
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[auth_get_db] = override_get_db

# # --- 5) לקוח טסטים יחיד
# client = TestClient(app)

# # --- 6) עוזר לזריעת משתמשים
# def seed_user(db, **fields):
#     if "id" in fields:
#         db.query(User).filter(User.id == fields["id"]).delete()
#     if "username" in fields:
#         db.query(User).filter(User.username == fields["username"]).delete()
#     db.commit()
#     u = User(**fields)
#     db.add(u)
#     db.commit()
#     db.refresh(u)
#     return u


# tests/utils.py
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

# --- 0) ודא ששורש הפרויקט ב-PYTHONPATH לפני הייבוא של app.*
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- 1) קבע ENV של טסטים BEFORE imports (כדי שהאפליקציה לא תנסה להתחבר לפרוד)
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")  # הכי נקי לטסטים
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# --- 2) עכשיו מותר לייבא את האפליקציה
from app.main import app
from app.database import Base
from app.routers.auth import get_db  # עדכן אם ה-dependency נמצא במקום אחר

# --- 3) בונים Engine לטסטים
TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # נדרש ל-SQLite
    poolclass=StaticPool,                       # יציב ל-:memory:
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 4) סכימה לטסטים
Base.metadata.create_all(bind=engine)

# --- 5) override ל-get_db כך שכל הראוטרים ירוצו על DB הטסטים
def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --- 6) לקוח טסטים
client = TestClient(app)

# --- 7) עזר לזריעת יוזר
from app.models import User  # הייבוא כאן כדי למנוע מעגליות מיותרת
def seed_user(db, **fields):
    if "id" in fields:
        db.query(User).filter(User.id == fields["id"]).delete()
    if "username" in fields:
        db.query(User).filter(User.username == fields["username"]).delete()
    db.commit()
    u = User(**fields)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

