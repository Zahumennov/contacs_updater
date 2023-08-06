from fastapi.testclient import TestClient

from core.views import app

client = TestClient(app)


def test_get_contacts_by_full_text():
    response = client.get("/contacts/", params={"keyword": "Craig"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
