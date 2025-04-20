import pytest

from aistente_visual.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_served(client):
    """Comprueba que GET / devuelve 200 y contiene el tag <video>."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<video" in response.data
