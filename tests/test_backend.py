from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_route():
    r = client.post("/api/agents/route", json={"message":"summarize this PDF"})
    assert r.status_code == 200
    assert r.json()["agent"] == "document"
