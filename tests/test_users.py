def test_register(client):
    """test registration"""
    response = client.post("/auth/register/",json={"username":"some","password":"12345678","balance":500})

    assert response.status_code == 200


def test_login(client):
    register_response = client.post("/auth/register/",json={"username":"some","password":"12345678","balance":500})
    assert register_response.status_code == 200

    response = client.post("/auth/login/",json={"username":"some","password":"12345678"})
    assert response.status_code == 200

def test_refresh_token(client):
    register_response = client.post("/auth/register/",json={"username":"some","password":"12345678","balance":500})
    assert register_response.status_code == 200

    login_response = client.post("/auth/login/",json={"username":"some","password":"12345678"})
    assert login_response.status_code == 200
    refresh_token = login_response.json()["token"]["refresh_token"]
    
    response = client.post("/auth/refresh/",json={"refresh_token":refresh_token})
    assert response.status_code == 200

    
def test_get_users(client,admin_login):
    response = client.get("/api/v1/users",headers=admin_login)
    assert response.status_code == 200


def test_change_role(client,admin_login):
    """to test this endpoint you must run celery  and rabbitmq"""
    register_response = client.post("/auth/register/",json={"username":"some","password":"12345678","balance":500})
    assert register_response.status_code == 200
    response = client.patch(f"/api/v1/users/role/{register_response.json()["user"]["id"]}",json={"role":"admin"},headers=admin_login)
    assert response.status_code == 200