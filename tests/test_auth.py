# #tests.test_auth file:
# from base64 import encode
# from datetime import timedelta

# from jose import jwt
# from starlette import status
# import pytest
# from ..routers.auth import get_db, authenticate_user, SECRET_KEY, ALGORITHM, create_access_token, get_current_user
# from .utils import app,override_get_db,TestingSession,client

# app.dependency_overrides[get_db]=override_get_db()




# def test_authenticate_user(test_Trainer):
#     db = TestingSession()
#     user_test=authenticate_user("Moriz","test1234",db)
#     assert user_test is not None
#     assert test_Trainer.username == user_test.username

#     wrong_user_test=authenticate_user("Moris","test1234",db)
#     assert wrong_user_test is False

#     wrong_password_test = authenticate_user("Moriz", "test123", db)
#     assert wrong_password_test is False

# def test_create_access_token():
#     username = "Moriz"
#     id=1
#     role='admin'
#     expires_delta = timedelta(minutes=15)

#     token= create_access_token(username,id,role,expires_delta)
#     decode_token=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM,options={"verify_signature":False})

#     assert decode_token.get('sub')==username
#     assert decode_token.get('id')==id
#     assert decode_token.get('role')==role

# @pytest.mark.asyncio
# async def test_get_current_user():
#     encoded_data= {"username": 'Moriz', "id": 1, "role": 'admin'}
#     token= jwt.encode(encoded_data,SECRET_KEY,algorithm=ALGORITHM)
#     user= await get_current_user(token)
#     assert user is not None
#     assert user["username"] =='Moriz'
#     assert user["id"]==1
#     assert user["role"]=='admin'


# def test_login_success(test_Trainer):
#     response = client.post(
#         "/auth/login",
#         data={
#             "username": "Moriz",
#             "password": "test1234"
#         }
#     )

#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert "access_token" in data
#     assert data["token_type"] == "bearer"

# def test_login_wrong_password(test_Trainer):
#     response = client.post(
#         "/auth/login",
#         data={
#             "username": "Moriz",
#             "password": "wrongpassword"
#         }
#     )
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.json() == {"detail": "Incorrect username or password"}

# def test_login_wrong_username(test_Trainer):
#     response = client.post(
#         "/auth/login",
#         data={
#             "username": "notexist",
#             "password": "test1234"
#         }
#     )
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.json() == {"detail": "Incorrect username or password"}