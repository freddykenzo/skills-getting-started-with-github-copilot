import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Fixture to reset activities before each test
@pytest.fixture(autouse=True)
def reset_activities():
    # Reset to original state
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })

def test_root_redirect():
    # Arrange: No special setup needed

    # Act: Make GET request to root without following redirects
    response = client.get("/", follow_redirects=False)

    # Assert: Should redirect to /static/index.html
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    # Arrange: Activities are reset by fixture

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Should return 200 and the activities dict
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert len(data["Chess Club"]["participants"]) == 2

def test_signup_success():
    # Arrange: Use a new email for Programming Class

    # Act: POST to signup
    response = client.post("/activities/Programming%20Class/signup?email=newstudent@mergington.edu")

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    # Verify added to activities
    assert "newstudent@mergington.edu" in activities["Programming Class"]["participants"]

def test_signup_activity_not_found():
    # Arrange: Use non-existent activity

    # Act: POST to signup
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")

    # Assert: Should return 404
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_signup_duplicate_email():
    # Arrange: Try to signup michael again for Chess Club

    # Act: POST to signup
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")

    # Assert: Should return 400
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is already signed up"

def test_signup_activity_full():
    # Arrange: Fill up an activity (Chess Club has max 12, currently 2)
    # Add more participants to reach max
    for i in range(10):
        activities["Chess Club"]["participants"].append(f"extra{i}@mergington.edu")

    # Act: Try to signup one more
    response = client.post("/activities/Chess%20Club/signup?email=overflow@mergington.edu")

    # Assert: Should return 400
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Activity is full"

def test_signup_invalid_email():
    # Arrange: Use email without @

    # Act: POST to signup
    response = client.post("/activities/Programming%20Class/signup?email=invalidemail")

    # Assert: Should return 400
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid email format"

def test_unregister_success():
    # Arrange: Unregister an existing participant

    # Act: DELETE to unregister
    response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]
    # Verify removed
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

def test_unregister_activity_not_found():
    # Arrange: Use non-existent activity

    # Act: DELETE to unregister
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")

    # Assert: Should return 404
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_participant_not_found():
    # Arrange: Try to unregister non-participant

    # Act: DELETE to unregister
    response = client.delete("/activities/Chess%20Club/unregister?email=nonparticipant@mergington.edu")

    # Assert: Should return 404
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"