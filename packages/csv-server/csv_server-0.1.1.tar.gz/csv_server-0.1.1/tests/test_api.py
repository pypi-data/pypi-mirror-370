import pytest
from fastapi.testclient import TestClient
from csv_server.app import create_app
from pathlib import Path
import shutil
import tempfile
import os

@pytest.fixture
def temp_data_dir():
    # Create a temp directory with a sample users.csv
    tmpdir = tempfile.mkdtemp()
    users_csv = os.path.join(tmpdir, "users.csv")
    with open(users_csv, "w") as f:
        f.write("id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com\n")
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)

@pytest.fixture
def client(temp_data_dir):
    app = create_app(temp_data_dir, readonly=False, config={
        "resources": {
            "users": {
                "file": "users.csv",
                "primary_key": "id",
                "readonly": False
            }
        }
    })
    return TestClient(app)

def test_list_users(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] == 2

def test_get_user(client):
    resp = client.get("/users/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"

def test_create_user(client):
    resp = client.post("/users", json={"name": "Charlie", "email": "charlie@example.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == "3"
    assert data["name"] == "Charlie"

def test_update_user(client):
    resp = client.put("/users/1", json={"name": "Alice Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice Updated"

def test_delete_user(client):
    resp = client.delete("/users/2")
    assert resp.status_code == 204
    # Confirm deletion
    resp2 = client.get("/users/2")
    assert resp2.status_code == 404