from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def make_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@example.com"


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_catalog():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "participants" in data[expected_activity]
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Programming Class"
    email = make_email("signup")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]

    client.delete(f"/activities/{activity_name}/unregister?email={email}")


def test_signup_duplicate_is_rejected():
    # Arrange
    activity_name = "Chess Club"
    email = make_email("duplicate")

    # Act
    first_signup = client.post(f"/activities/{activity_name}/signup?email={email}")
    second_signup = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert first_signup.status_code == 200
    assert second_signup.status_code == 400
    assert "already signed up" in second_signup.json()["detail"].lower()

    client.delete(f"/activities/{activity_name}/unregister?email={email}")


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Gym Class"
    email = make_email("remove")

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    delete_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert "Removed" in delete_response.json()["message"]

    verify_response = client.get("/activities")
    assert email not in verify_response.json()[activity_name]["participants"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = make_email("missing")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unknown_participant_returns_404():
    # Arrange
    activity_name = "Basketball Club"
    email = make_email("missing")

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()

