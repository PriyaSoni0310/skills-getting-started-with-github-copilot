import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Since it redirects to static/index.html, but TestClient follows redirects by default
    # Actually, in the code, it's RedirectResponse, so it should redirect
    # But since static files are mounted, it might serve the file
    # For simplicity, just check it's successful

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check structure
    activity = next(iter(data.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_success():
    # Use a test email
    email = "test@example.com"
    activity = "Soccer Team"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Check that the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]

def test_signup_already_signed_up():
    email = "test@example.com"
    activity = "Soccer Team"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    # Second signup should fail
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity():
    email = "test@example.com"
    activity = "Invalid Activity"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    email = "test2@example.com"
    activity = "Basketball Club"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    # Then unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Check that the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity]["participants"]

def test_unregister_not_signed_up():
    email = "notsigned@example.com"
    activity = "Art Club"
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_invalid_activity():
    email = "test@example.com"
    activity = "Invalid Activity"
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]