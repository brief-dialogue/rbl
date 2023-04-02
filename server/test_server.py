from fastapi.testclient import TestClient

from server.server import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == '"working fine"'


def test_validate():
    response = client.post("/erc",
                           json={
                               "answer": "foo",
                               "expectedAns": "The Foo ID Stealers",
                           })
    assert response.status_code == 200
    assert response.json() == {"score": "0.369"}
