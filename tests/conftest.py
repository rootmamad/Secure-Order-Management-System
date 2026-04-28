from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
from main import app
from database import get_session
from fastapi.testclient import TestClient
from utils import create_hash
from models import Users
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False},poolclass=StaticPool)

TestSessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

def override_get_session():
    db = TestSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        print("a problem: ",e)
        db.rollback()
        raise e
    finally:
        db.close()

@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="function")
def client():
    with TestClient(app=app, raise_server_exceptions=False) as c:
        yield c


        





@pytest.fixture(scope="function",autouse=True)
def setup_database():
    from database import Base 
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_login(client):
    response =client.post("/auth/register", json={"username": "mmdy", "password": "12345678", "balance": 1000})
    
    
    token = response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_login(client,db_session):
    
    
    admin_password =  create_hash("1234")
    admin_user = Users(
        username="admin_user",
        full_name="Admin Admin",
        balance=20,
        hashed_password=admin_password,
        role="admin"
    )
    db_session.add(admin_user)

    db_session.commit()
    db_session.refresh(admin_user)
    response = client.post("/auth/login/", json={
        "username": "admin_user",
        "password": "1234"
    })
    token = response.json()["token"]["access_token"]
    

    return {"Authorization": f"Bearer {token}"}