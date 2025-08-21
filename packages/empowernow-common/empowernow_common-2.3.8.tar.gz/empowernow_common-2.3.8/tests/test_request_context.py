import json
from fastapi import Request
from fastapi.testclient import TestClient
from fastapi import FastAPI

from empowernow_common.fastapi import request_context

app = FastAPI()

@app.post("/ctx")
async def ctx(request: Request):
    return await request_context(request, include_headers=True, include_body=True, max_body_bytes=10)

def test_request_context_extractor():
    client = TestClient(app)
    r = client.post("/ctx?x=1", json={"hello": "world"}, headers={"Authorization": "Bearer abc", "User-Agent": "pytest"})
    assert r.status_code == 200
    ctx = r.json()
    assert ctx["ip"]
    assert ctx["user_agent"] == "pytest"
    # Sensitive header masked
    assert ctx["headers"]["authorization"] == "***redacted***"
    # Body truncated
    assert ctx["body"].endswith("...") 