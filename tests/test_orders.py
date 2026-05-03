def test_add_to_cart(client, admin_login, user_login):
    creat_response = client.post(
        "/api/v1/items/create/",
        json={"name": "Laptop", "price": 50, "quantity": 10},
        headers=admin_login,
    )
    assert creat_response.status_code == 200
    response = client.post(
        f"/api/v1/orders/item/{creat_response.json()["id"]}/add-to-cart",
        params={"quantity": 1},
        headers=user_login,
    )
    assert response.status_code == 200


def test_get_order(client, user_login, admin_login):
    creat_response = client.post(
        "/api/v1/items/create/",
        json={"name": "Laptop", "price": 50, "quantity": 10},
        headers=admin_login,
    )
    assert creat_response.status_code == 200
    add_response = client.post(
        f"/api/v1/orders/item/{creat_response.json()["id"]}/add-to-cart",
        params={"quantity": 1},
        headers=user_login,
    )
    assert add_response.status_code == 200
    response = client.get(f"/api/v1/orders/order/{1}", headers=user_login)
    assert response.status_code == 200


def test_checkout(client, admin_login, user_login):
    creat_response = client.post(
        "/api/v1/items/create/",
        json={"name": "Laptop", "price": 50, "quantity": 10},
        headers=admin_login,
    )
    assert creat_response.status_code == 200
    add_response = client.post(
        f"/api/v1/orders/item/{creat_response.json()["id"]}/add-to-cart",
        params={"quantity": 1},
        headers=user_login,
    )
    assert add_response.status_code == 200
    response = client.post(f"/api/v1/orders/order/{1}/checkout", headers=user_login)
    assert response.status_code == 200


def test_return(client, admin_login, user_login):
    creat_response = client.post(
        "/api/v1/items/create/",
        json={"name": "Laptop", "price": 50, "quantity": 10},
        headers=admin_login,
    )
    assert creat_response.status_code == 200
    add_response = client.post(
        f"/api/v1/orders/item/{creat_response.json()["id"]}/add-to-cart",
        params={"quantity": 1},
        headers=user_login,
    )
    assert add_response.status_code == 200
    order_response = client.post(
        f"/api/v1/orders/order/{1}/checkout", headers=user_login
    )
    assert order_response.status_code == 200
    response = client.post(
        f"/api/v1/orders/item/{1}/return", params={"quantity": 1}, headers=user_login
    )
    assert response.status_code == 200


def test_cancel(client, admin_login, user_login):
    creat_response = client.post(
        "/api/v1/items/create/",
        json={"name": "Laptop", "price": 50, "quantity": 10},
        headers=admin_login,
    )
    assert creat_response.status_code == 200
    add_response = client.post(
        f"/api/v1/orders/item/{creat_response.json()["id"]}/add-to-cart",
        params={"quantity": 1},
        headers=user_login,
    )
    assert add_response.status_code == 200
    response = client.patch(f"/api/v1/orders/order/{1}/cancel", headers=user_login)
    assert response.status_code == 200
