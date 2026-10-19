import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client 


def test_create_case(client):
    response = client.post(
        "/cases",
        json={
            "description": "My internet connection is down"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "case" in data
    assert "a2a_response" in data
    assert data["case"]["category"] == "network"
    assert data["case"]["assigned_team"] == "network_team"


def test_get_existing_case(client):
    create_response = client.post(
        "/cases",
        json={
            "description": "I was charged twice for my subscription"
        },
    )

    assert create_response.status_code == 200

    case_id = create_response.json()["case"]["case_id"]

    get_response = client.get(f"/cases/{case_id}")

    assert get_response.status_code == 200
    assert get_response.json()["case_id"] == case_id


def test_get_nonexistent_case(client):
    response = client.get("/cases/nonexistent-case-12345")

    assert response.status_code == 404


def test_empty_description(client):
    response = client.post(
        "/cases",
        json={"description": ""},
    )

    assert response.status_code == 422


from unittest.mock import patch


def test_workflow_value_error(client):
    with patch(
        "main.case_graph.invoke",
        side_effect=ValueError("Invalid case category"),
    ):
        response = client.post(
            "/cases",
            json={
                "description": "Please investigate my support issue"
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid case category"

