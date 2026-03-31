import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Save original state
    original_activities = copy.deepcopy(activities)
    yield
    # Teardown: Restore original state
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    # Arrange
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 200
    assert "Mergington High School" in response.text  # Check if static file is served


def test_get_activities(client):
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_existing_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    # Verify participant added
    response2 = client.get("/activities")
    assert email in response2.json()[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}


def test_signup_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Exists in participants
    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    # Verify participant removed
    response2 = client.get("/activities")
    assert email not in response2.json()[activity_name]["participants"]


def test_remove_participant_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"  # Not in participants
    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in activity"}


def test_remove_from_nonexistent_activity_404(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}