import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_system_status():
    response = client.get("/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "backend" in data
    assert data["backend"] == "online"
    assert "groq_api_key_set" in data
    assert "llm_provider" in data
    assert data["llm_provider"] == "groq"
    assert "embedding_provider" in data
    assert data["embedding_provider"] == "huggingface"
    assert "llm_model" in data
    assert "embedding_model" in data
    assert "total_chunks" in data


def test_ask_validation_min_length():
    response = client.get("/ask?query=hi")
    assert response.status_code == 422


def test_ask_endpoint_rate_limiting():
    for _ in range(25):
        res = client.get("/ask?query=testquery123")
        if res.status_code == 429:
            break

    assert res.status_code == 429, "Rate limiter did not trigger (429)"


def test_list_documents():
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "count" in data


def test_delete_nonexistent_document():
    response = client.delete("/documents/nonexistent_file.pdf")
    assert response.status_code == 404
