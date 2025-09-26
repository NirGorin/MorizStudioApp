# #test.test_admin file:
# from .utils import client, app, TestingSession, override_get_current_user, override_get_db, Limitation
# from sqlalchemy import text
# from fastapi import status

# from .test_trainers import override_get_db,override_get_current_user
# from ..routers.auth import get_current_user, get_db

# app.dependency_overrides[get_current_user]=override_get_current_user
# app.dependency_overrides[get_db]=override_get_db


# def override_get_current_user_not_admin():
#     return {'username': 'Moriz', 'id': 1, 'role': 'user'}

# def test_admin_get_limitations(test_Limitation):
#     response = client.get("/admin/limitations")
#     assert response.status_code == 200
#     assert response.json() == [{'ID':1,
#                             'limitation':"Pregnancy"}]

# def test_not_admin_get_limitations(test_Limitation):
#     app.dependency_overrides[get_current_user]=override_get_current_user_not_admin
#     response = client.get("/admin/limitations")
#     assert response.status_code ==403
#     app.dependency_overrides[get_current_user] = override_get_current_user

# def test_admin_post_limitations(test_Limitation):
#     request_limitation= {'limitation':"Pregnancy"}
#     response = client.post("/admin/limitations", json=request_limitation)
#     assert response.status_code == 201
#     db=TestingSession()
#     limitation_model=db.query(Limitation).filter(Limitation.ID==2).first()
#     assert limitation_model.limitation == request_limitation['limitation']
#     db.execute(text("DELETE FROM limitations;"))
#     db.commit()

# def test_not_admin_post_limitations(test_Limitation):
#     app.dependency_overrides[get_current_user] = override_get_current_user_not_admin
#     request_limitation = {'limitation': "Pregnancy"}
#     response = client.post("/admin/limitations",json=request_limitation)
#     assert response.status_code == 403
#     app.dependency_overrides[get_current_user] = override_get_current_user
#     db=TestingSession()
#     db.execute(text("DELETE FROM limitations;"))
#     db.commit()




