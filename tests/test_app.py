from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_signup_duplicate_is_rejected():
    activity_name = "Chess Club"
    email = "duplicate-test@example.com"

    first_signup = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first_signup.status_code == 200

    second_signup = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert second_signup.status_code == 400
    assert "already signed up" in second_signup.json()["detail"].lower()

    delete_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert delete_response.status_code == 200


def test_unregister_removes_participant():
    activity_name = "Gym Class"
    email = "remove-test@example.com"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert "Removed" in data["message"]

    verify_response = client.get("/activities")
    assert email not in verify_response.json()[activity_name]["participants"]
