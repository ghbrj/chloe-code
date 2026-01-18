# tests/test_endpoints.py
def test_health(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_infer_success(client):
    payload = {
        "prompt": "Create a Python function that returns the factorial of n",
        "file_path": None,
        "language": "python"
    }
    r = client.post("/v1/infer", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "code" in data
    assert isinstance(data["latency_ms"], int)

def test_search_empty(client):
    r = client.get("/v1/search", params={"q": "nothing", "k": 3})
    assert r.status_code == 200
    assert "results" in r.json()