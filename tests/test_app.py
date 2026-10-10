def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_healthz(client):
    response = client.get("/api/healthz")
    assert response.json["status"] == "ok"


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_wrong_password(client, admin):
    response = client.post("/login", data={"username": "admin", "password": "wrong"})
    assert response.status_code == 200
    assert "ไม่ถูกต้อง".encode() in response.data


def test_admin_can_list_users(admin_client):
    response = admin_client.get("/users")
    assert response.status_code == 200
    assert b"admin" in response.data


def test_admin_can_create_user(admin_client):
    from app_name import models

    response = admin_client.post(
        "/users/create",
        data={
            "username": "staff01",
            "password": "password1234",
            "first_name": "Staff",
            "last_name": "One",
            "email": "staff01@example.com",
            "roles": ["user"],
        },
    )
    assert response.status_code == 302
    user = models.User.objects(username="staff01").first()
    assert user.check_password("password1234")
    assert user.roles == ["user"]


def test_open_redirect_is_blocked(client, admin):
    client.get("/login?next=https://evil.example.com")
    response = client.post(
        "/login", data={"username": "admin", "password": "password1234"}
    )
    assert response.headers["Location"] == "/"


def test_admin_can_edit_user(admin_client):
    from app_name import models

    user = models.User(username="staff01", roles=["user"]).save()
    response = admin_client.post(
        f"/users/{user.id}/edit",
        data={"username": "staff01", "first_name": "Edited", "roles": ["user"]},
    )
    assert response.status_code == 302
    user.reload()
    assert user.first_name == "Edited"


def test_admin_can_deactivate_user(admin_client):
    from app_name import models

    user = models.User(username="staff01", roles=["user"]).save()
    response = admin_client.post(f"/users/{user.id}/deactivate")
    assert response.status_code == 302
    user.reload()
    assert user.status == "inactive"

