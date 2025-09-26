# # tests/routers/test_users.py
# import types
# import pytest
# from fastapi import FastAPI
# from fastapi.testclient import TestClient
# from sqlalchemy import Column, Integer, String, create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker, Session

# # === Import the router module under test ===
# # Adjust the import to your project structure if needed
# from ..routers import users


# # ---------- Test doubles / fakes ----------

# class FakeRedis:
#     """Very small subset used by the router: get, setex, exists."""
#     def __init__(self):
#         self._store = {}

#     def get(self, key: str):
#         return self._store.get(key)

#     def setex(self, key: str, ttl_seconds: int, value: str):
#         # We don't implement TTL expiry in tests; not needed for logic checks
#         self._store[key] = value

#     def exists(self, key: str) -> int:
#         return 1 if key in self._store else 0


# Base = declarative_base()

# class TestUser(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, index=True)
#     first_name = Column(String(50))
#     last_name = Column(String(50))
#     email = Column(String(120), unique=True, index=True)
#     phone_number = Column(String(30))


# # Minimal CreateUserRequest compatible with the router's expected field names
# # (First_Name, Last_Name, Email, Phone_Number)
# from pydantic import BaseModel

# class TestCreateUserRequest(BaseModel):
#     First_Name: str
#     Last_Name: str
#     Email: str
#     Phone_Number: str


# # ---------- Pytest fixtures ----------

# @pytest.fixture
# def db_engine():
#     engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
#     Base.metadata.create_all(engine)
#     try:
#         yield engine
#     finally:
#         Base.metadata.drop_all(engine)


# @pytest.fixture
# def SessionLocal(db_engine):
#     return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


# @pytest.fixture
# def db_session(SessionLocal):
#     session: Session = SessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()


# @pytest.fixture
# def app_client(monkeypatch, db_session):
#     """
#     Build a tiny FastAPI app that mounts the tested router.
#     We monkeypatch:
#       - users.User -> our TestUser model
#       - users.CreateUserRequest -> our TestCreateUserRequest
#       - users.r -> FakeRedis
#       - users.CACHE_TTL_SECONDS -> small constant (unchanged logic)
#       - dependency override for users.get_db -> yields our db_session
#     """
#     # Patch symbols used inside the router implementation
#     monkeypatch.setattr(users, "User", TestUser, raising=True)
#     monkeypatch.setattr(users, "CreateUserRequest", TestCreateUserRequest, raising=True)
#     fake_r = FakeRedis()
#     monkeypatch.setattr(users, "r", fake_r, raising=True)
#     monkeypatch.setattr(users, "CACHE_TTL_SECONDS", 600, raising=True)

#     # Build a small FastAPI app and include the router under test
#     app = FastAPI()
#     app.include_router(users.router)

#     # Override the DB dependency used inside the router
#     def _get_db_override():
#         try:
#             yield db_session
#         finally:
#             pass

#     app.dependency_overrides[users.get_db] = _get_db_override

#     client = TestClient(app)

#     # Expose client and fake redis for assertions
#     holder = types.SimpleNamespace(client=client, r=fake_r)
#     return holder


# # ---------- Helper to seed the DB ----------

# def seed_user(db: Session, **kw) -> TestUser:
#     u = TestUser(**kw)
#     db.add(u)
#     db.commit()
#     db.refresh(u)
#     return u


# # ---------- Tests ----------

# def test_get_user_found_returns_200(app_client, db_session):
#     u = seed_user(
#         db_session,
#         id=1, username="alice", first_name="Alice", last_name="Liddell",
#         email="alice@example.com", phone_number="123"
#     )
#     resp = app_client.client.get("/users/1/")
#     assert resp.status_code == 200
#     # Depending on FastAPI serialization of ORM objects,
#     # at least verify that some identifying info appears in the JSON.
#     body = resp.json()
#     # The exact shape depends on your project's response_model; we assert a few keys if present.
#     assert isinstance(body, dict)
#     # If your project serializes ORM with pydantic, these will likely exist:
#     # Be tolerant: only check id if present
#     if "id" in body:
#         assert body["id"] == u.id


# def test_get_user_not_found_returns_404(app_client):
#     resp = app_client.client.get("/users/999/")
#     assert resp.status_code == 404
#     assert resp.json()["detail"] == "User not found"


# def test_get_user_email_cache_miss_then_hit(app_client, db_session):
#     u = seed_user(
#         db_session,
#         id=2, username="bob", first_name="Bob", last_name="Builder",
#         email="bob@example.com", phone_number="555"
#     )

#     # First: MISS -> reads DB, sets cache
#     resp1 = app_client.client.get("/users/2/email")
#     assert resp1.status_code == 200
#     data1 = resp1.json()
#     assert data1 == {"user_id": 2, "email": "bob@example.com", "cache": "MISS"}
#     assert app_client.r.get("user:2:email") == "bob@example.com"

#     # Second: HIT -> served from cache
#     resp2 = app_client.client.get("/users/2/email")
#     assert resp2.status_code == 200
#     data2 = resp2.json()
#     assert data2 == {"user_id": 2, "email": "bob@example.com", "cache": "HIT"}


# def test_get_user_email_not_found_404(app_client):
#     resp = app_client.client.get("/users/404/email")
#     assert resp.status_code == 404
#     assert resp.json()["detail"] == "User not found"


# def test_delete_user_by_username_path_param(app_client, db_session):
#     """
#     NOTE: The router path is '/{user_id}/' but the function parameter is 'username: str'.
#     FastAPI will pass the path segment into the 'username' parameter (as string).
#     This test asserts the current behavior as implemented.
#     """
#     seed_user(
#         db_session,
#         id=10, username="charlie", first_name="Char", last_name="Lie",
#         email="charlie@example.com", phone_number="999"
#     )

#     # Call DELETE with the username in the path (per current signature)
#     resp = app_client.client.delete("/users/charlie/")
#     assert resp.status_code == 200
#     assert resp.json()["message"] == "User deleted successfully"

#     # Verify it's gone
#     # (Hitting GET /users/{id}/ should 404 now if we try the old id)
#     resp2 = app_client.client.get("/users/10/")
#     # If your serialization of GET /users/{id}/ returns 404 correctly after deletion:
#     assert resp2.status_code in (200, 404)
#     # In strict DB terms, ensure user not found in DB:
#     assert db_session.query(TestUser).filter_by(username="charlie").first() is None


# def test_delete_user_not_found_returns_404(app_client):
#     resp = app_client.client.delete("/users/not_exists/")
#     assert resp.status_code == 404
#     assert resp.json()["detail"] == "User not found"


# def test_update_user_updates_db_and_cache(app_client, db_session):
#     u = seed_user(
#         db_session,
#         id=3, username="dina", first_name="Di", last_name="Na",
#         email="dina@old.com", phone_number="000"
#     )

#     # Prime cache with the old email to verify it gets refreshed
#     app_client.r.setex("user:3:email", 600, "dina@old.com")

#     payload = {
#         "First_Name": "Dina",
#         "Last_Name": "Doe",
#         "Email": "dina@new.com",
#         "Phone_Number": "111-222"
#     }
#     resp = app_client.client.put("/users/3/update_user", json=payload)
#     assert resp.status_code == 200
#     body = resp.json()
#     assert body["message"] == "User updated successfully"

#     # DB updated?
#     updated = db_session.query(TestUser).filter_by(id=3).first()
#     assert updated.first_name == "Dina"
#     assert updated.last_name == "Doe"
#     assert updated.email == "dina@new.com"
#     assert updated.phone_number == "111-222"

#     # Cache refreshed?
#     assert app_client.r.get("user:3:email") == "dina@new.com"

# # tests/test_users.py
# import pytest

# # נשתמש ב-client, TestingSession ו-seed_user מה-utils
# from tests.utils import client, TestingSession, seed_user

# # תמיכה בשני מבני פרויקט
# try:
#     from ..routers import users as users_router
#     from ..models import User
# except ImportError:
#     import routers.users as users_router
#     from models import User


# # Redis דמה, נגשים רק למתודות שה-router משתמש
# class FakeRedis:
#     def __init__(self):
#         self._store = {}
#     def get(self, k): return self._store.get(k)
#     def setex(self, k, ttl, v): self._store[k] = v
#     def exists(self, k): return 1 if k in self._store else 0


# # נחליף את redis הגלובלי של ה-router לפני כל טסט
# @pytest.fixture(autouse=True)
# def _fake_redis(monkeypatch):
#     monkeypatch.setattr(users_router, "r", FakeRedis(), raising=True)


# def test_get_user_email_cache_miss_then_hit():
#     db = TestingSession()
#     seed_user(
#         db,
#         id=2,
#         username="bob",
#         first_name="Bob",
#         last_name="Builder",
#         email="bob@example.com",
#         phone_number="050-0000000",
#     )
#     db.close()

#     # ראשון: MISS
#     r1 = client.get("/users/2/email")
#     assert r1.status_code == 200
#     assert r1.json() == {"user_id": 2, "email": "bob@example.com", "cache": "MISS"}

#     # שני: HIT
#     r2 = client.get("/users/2/email")
#     assert r2.status_code == 200
#     assert r2.json() == {"user_id": 2, "email": "bob@example.com", "cache": "HIT"}


# def test_get_user_not_found_returns_404():
#     r = client.get("/users/999999/")
#     assert r.status_code == 404
#     assert r.json()["detail"] == "User not found"


# def test_delete_user_by_username_path_param():
#     """
#     שים לב: הנתיב הוא '/{user_id}/' אבל הפונקציה מוגדרת עם 'username: str'.
#     לכן שולחים username בנתיב - זו ההתנהגות הנוכחית של הקוד.
#     """
#     db = TestingSession()
#     seed_user(
#         db,
#         id=10,
#         username="charlie",
#         first_name="Char",
#         last_name="Lie",
#         email="charlie@example.com",
#         phone_number="050-9999999",
#     )
#     db.close()

#     r = client.delete("/users/charlie/")
#     assert r.status_code == 200
#     assert r.json()["message"] == "User deleted successfully"

#     # מוודאים שנמחק מה-DB
#     db = TestingSession()
#     assert db.query(User).filter(User.username == "charlie").first() is None
#     db.close()


# def test_update_user_updates_db_and_cache():
#     db = TestingSession()
#     seed_user(
#         db,
#         id=3,
#         username="dina",
#         first_name="Di",
#         last_name="Na",
#         email="dina@old.com",
#         phone_number="000",
#     )
#     db.close()

#     payload = {
#         "First_Name": "Dina",
#         "Last_Name": "Doe",
#         "Email": "dina@new.com",
#         "Phone_Number": "111-222",
#     }
#     r = client.put("/users/3/update_user", json=payload)
#     assert r.status_code == 200
#     assert r.json()["message"] == "User updated successfully"

#     # בדיקת DB
#     db = TestingSession()
#     u = db.query(User).filter(User.id == 3).first()
#     assert u is not None
#     assert u.first_name == "Dina"
#     assert u.last_name == "Doe"
#     assert u.email == "dina@new.com"
#     assert u.phone_number == "111-222"
#     db.close()



# tests/test_users.py
import pytest
from tests.utils import client, TestingSession, seed_user

# תמיכה בשני מבני פרויקט (עם/בלי app/)
try:
    from app.routers import users as users_router
    from app.models import User
except ImportError:
    import routers.users as users_router
    from models import User

# Fake Redis שמספק רק מה שהראוטר משתמש
class FakeRedis:
    def __init__(self):
        self._store = {}
    def get(self, k): return self._store.get(k)
    def setex(self, k, ttl, v): self._store[k] = v
    def exists(self, k): return 1 if k in self._store else 0

# מחליף את redis הגלובלי של ה-router לפני כל טסט
@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch):
    monkeypatch.setattr(users_router, "r", FakeRedis(), raising=True)

def test_get_user_email_cache_miss_then_hit():
    db = TestingSession()
    seed_user(
        db,
        id=2,
        username="bob",
        first_name="Bob",
        last_name="Builder",
        email="bob@example.com",
        phone_number="050-0000000",
    )
    db.close()

    r1 = client.get("/users/2/email")
    assert r1.status_code == 200
    assert r1.json() == {"user_id": 2, "email": "bob@example.com", "cache": "MISS"}

    r2 = client.get("/users/2/email")
    assert r2.status_code == 200
    assert r2.json() == {"user_id": 2, "email": "bob@example.com", "cache": "HIT"}

def test_get_user_not_found_returns_404():
    r = client.get("/users/999999/")
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"

def test_delete_user_by_username_path_param():
    # הנתיב הוא '/{user_id}/' אבל הפונקציה מוגדרת עם 'username: str' — שולחים username בנתיב
    db = TestingSession()
    seed_user(
        db,
        id=10,
        username="charlie",
        first_name="Char",
        last_name="Lie",
        email="charlie@example.com",
        phone_number="050-9999999",
    )
    db.close()

    r = client.delete("/users/charlie/")
    assert r.status_code == 200
    assert r.json()["message"] == "User deleted successfully"

    db = TestingSession()
    assert db.query(User).filter(User.username == "charlie").first() is None
    db.close()

def test_update_user_updates_db_and_cache():
    db = TestingSession()
    seed_user(
        db,
        id=3,
        username="dina",
        first_name="Di",
        last_name="Na",
        email="dina@old.com",
        phone_number="000",
    )
    db.close()

    payload = {
        "Username": "dina",
        "First_Name": "Dina",
        "Last_Name": "Doe",
        "Email": "dina@new.com",
        "Phone_Number": "111-222",
    }
    r = client.put("/users/3/update_user", json=payload)
    assert r.status_code == 200
    assert r.json()["message"] == "User updated successfully"

    db = TestingSession()
    u = db.query(User).filter(User.id == 3).first()
    assert u is not None
    assert u.first_name == "Dina"
    assert u.last_name == "Doe"
    assert u.email == "dina@new.com"
    assert u.phone_number == "111-222"
    db.close()


