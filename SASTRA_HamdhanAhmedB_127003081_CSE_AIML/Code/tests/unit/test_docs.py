import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_create_project():
    response = client.post("/api/v1/projects/", json={"name": "Test Project", "description": "A test project"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

def test_get_projects():
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_invalid_file():
    # Attempt to upload a non-pdf file
    # First get a project
    response = client.post("/api/v1/projects/", json={"name": "Upload Test Project"})
    project_id = response.json()["id"]

    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = client.post(f"/api/v1/projects/{project_id}/documents", files=files)
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]
