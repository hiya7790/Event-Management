def test_signup(client):
    response = client.post(
        "/users/signup",
        json={"username": "newuser", "email": "new@example.com", "password": "password", "is_admin": False}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"

def test_login(client, test_user):
    response = client.post(
        "/users/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_event_unauthorized(client, user_token):
    response = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Test Event", "description": "Desc", "date": "2024-12-01T10:00:00", "location": "Online"}
    )
    assert response.status_code == 403

def test_create_event_admin(client, admin_token):
    response = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Test Event", "description": "Desc", "date": "2024-12-01T10:00:00", "location": "Online"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Event"
    return response.json()["id"]

def test_register_for_event(client, admin_token, user_token):
    # Create event as admin
    event_response = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Event 1", "description": "Desc", "date": "2024-12-01T10:00:00", "location": "Online"}
    )
    event_id = event_response.json()["id"]

    # Register as user
    reg_response = client.post(
        f"/events/{event_id}/register",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"team_code": "ALPHA_TEAM"}
    )
    assert reg_response.status_code == 200
    assert reg_response.json()["event_id"] == event_id

def test_admin_mark_attendance(client, admin_token, user_token):
    # Create event
    event_response = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Event 2", "description": "Desc", "date": "2024-12-01T10:00:00", "location": "Online"}
    )
    event_id = event_response.json()["id"]

    # Register
    reg_response = client.post(
        f"/events/{event_id}/register",
        headers={"Authorization": f"Bearer {user_token}"},
        json={}
    )
    reg_id = reg_response.json()["id"]

    # Admin mark attendance
    attend_response = client.post(
        f"/admin/registrations/{reg_id}/attend",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert attend_response.status_code == 200
    assert attend_response.json()["attended"] == True

def test_get_qr_code(client, admin_token, user_token):
    event_response = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Event QR", "description": "Desc", "date": "2024-12-01T10:00:00", "location": "Online"}
    )
    event_id = event_response.json()["id"]

    reg_response = client.post(
        f"/events/{event_id}/register",
        headers={"Authorization": f"Bearer {user_token}"},
        json={}
    )
    reg_id = reg_response.json()["id"]

    qr_response = client.get(
        f"/registrations/{reg_id}/qr",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert qr_response.status_code == 200
    assert qr_response.headers["content-type"] == "image/png"
