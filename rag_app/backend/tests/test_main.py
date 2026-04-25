import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_index():
    response = client.get("/")
    assert response.status_code == 200

def test_llm_providers():
    response = client.get("/api/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data

def test_upload_invalid_format():
    response = client.post("/api/upload", files=[("file", ("test.exe", b"content"))])
    assert response.status_code == 400