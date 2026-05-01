import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models.database import Base
from models import models

SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def clean_db():
    """Очищает все таблицы в тестовой БД перед каждым тестом"""
    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    yield

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user(client):
    response = client.post("/users", json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    return response.json()

@pytest.fixture
def test_token(client, test_user):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    })
    return response.json()['access_token']

@pytest.fixture
def auth_headers(test_token):
    return {'Authorization': f'Bearer {test_token}'}