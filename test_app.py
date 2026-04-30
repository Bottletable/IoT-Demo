import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_ping(client):
    """Tjekker om ping-ruten virker"""
    rv = client.get('/ping')
    assert rv.status_code == 200
    assert b"pong" in rv.data