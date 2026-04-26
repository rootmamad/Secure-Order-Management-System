def test_create_item(client,admin_login):
    """test create endpoint"""
    response = client.post("/api/v1/items/create/", json={"name": "Laptop", "price": 500, "quantity": 10},headers=admin_login)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 500.0
    assert data["quantity"] == 10


def test_read_item_not_found(client,admin_login):
    """test for item that not exist"""
    response = client.get("/api/v1/items/item/999", headers=admin_login)
    assert response.status_code == 404

def test_delete_not_exist_item(client,admin_login):
    """"test for deleting an item that not exist"""
    response = client.post("/api/v1/items/delete/",params={"item_id":898},headers=admin_login)
    assert response.status_code == 404


def test_delete_item(client,admin_login):
    """"test for deleting an item"""
    
    created_item = client.post("/api/v1/items/create/", json={"name": "Laptop", "price": 500, "quantity": 10},headers=admin_login)
    assert created_item.status_code == 200
    
    created_item_id = created_item.json()["id"]
    response = client.post("/api/v1/items/delete/",params={"item_id":created_item_id},headers=admin_login)
    assert response.status_code == 200



'''def test_my_items_list(auth_headers):
    """تست مشاهده لیست خریدهای کاربر"""
    client.post("/create/", json={"name": "Monitor", "price": 200, "quantity": 10})
    client.post("/item/1/buy?quantity=1", headers=auth_headers)
    
    response = client.get("/myitem", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["item"]["name"] == "Monitor"'''