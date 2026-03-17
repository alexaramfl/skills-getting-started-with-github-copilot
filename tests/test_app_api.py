import copy
import pytest

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activity state before each test to avoid side effects."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_get_activities():
    # Arrange: baseline state from fixture
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "Programming Class" in payload


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_activity_full():
    # Arrange
    activity_name = "Debate Team"
    activities[activity_name]["participants"] = [f"user{i}@mergington.edu" for i in range(14)]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": "overflow@mergington.edu"}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is already full"


def test_remove_participant_success():
    # Arrange
    activity_name = "Tennis Club"
    participant = "alex@mergington.edu"
    assert participant in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": participant}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant} from {activity_name}"}
    assert participant not in activities[activity_name]["participants"]


def test_remove_participant_not_found():
    # Arrange
    activity_name = "Tennis Club"
    missing_email = "ghost@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": missing_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
