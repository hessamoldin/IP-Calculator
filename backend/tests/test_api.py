import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as c:
        yield c


def test_subnet_ok(client):
    r = client.post("/api/subnet", json={"input": "172.16.2.12/24"})
    assert r.status_code == 200 and r.json()["network"] == "172.16.2.0"


def test_subnet_bad_input(client):
    r = client.post("/api/subnet", json={"input": "nope"})
    assert r.status_code == 422


def test_history_roundtrip(client):
    client.post("/api/convert", json={"value": "10.0.0.1"})
    h = client.get("/api/history").json()
    assert h[0]["kind"] == "convert" and h[0]["input"] == "10.0.0.1"
    client.delete("/api/history")
    assert client.get("/api/history").json() == []


def test_vlsm_and_supernet(client):
    v = client.post("/api/vlsm", json={"network": "10.0.0.0/24",
                                       "requirements": [{"name": "a", "hosts": 50}]})
    assert v.json()["allocations"][0]["cidr"] == "10.0.0.0/26"
    s = client.post("/api/supernet", json={"networks": ["10.0.0.0/24", "10.0.1.0/24"]})
    assert s.json()["summary"]["cidr"] == "10.0.0.0/23"
