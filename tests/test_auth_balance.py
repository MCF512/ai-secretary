from app.db.base import SessionLocal
from app.models.user import UserDB


def test_register_and_login_user(client):
    register_payload = {
        "name": "Test User",
        "email": "test_user@example.com",
        "password": "password123",
        "telegram_id": None,
    }

    r = client.post("/auth/register", json=register_payload)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == register_payload["email"]
    assert data["balance"] == 0.0

    login_payload = {
        "email": register_payload["email"],
        "password": register_payload["password"],
    }
    r = client.post("/auth/login", json=login_payload)
    assert r.status_code == 200
    token_data = r.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == register_payload["email"]


def test_user_cannot_self_deposit_balance(client):
    payload = {
        "name": "User No Deposit",
        "email": "no_deposit@example.com",
        "password": "password123",
        "telegram_id": None,
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201

    r = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/users/me/balance/deposit",
        headers=headers,
        json={"amount": 50.0, "description": "Пополнение"},
    )
    assert r.status_code == 403


def test_admin_can_deposit_to_user_balance(client):
    session = SessionLocal()
    try:
        user = UserDB(
            id="test-user-id",
            telegram_id=None,
            name="Balance User",
            email="balance_user@example.com",
            hashed_password="dummy",
            role="user",
            balance=0.0,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    finally:
        session.close()

    r = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert r.status_code == 200
    admin_token = r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    r = client.post(
        f"/admin/users/{user_id}/balance/deposit",
        headers=admin_headers,
        json={"amount": 100.0, "description": "Тестовое пополнение"},
    )
    assert r.status_code == 200
    tx = r.json()
    assert tx["amount"] == 100.0
    assert tx["type"] == "deposit"

    r = client.post(
        "/auth/login",
        json={"email": "balance_user@example.com", "password": "password"},
    )
    assert r.status_code in (401, 404)

    session = SessionLocal()
    try:
        user = session.query(UserDB).filter(UserDB.id == user_id).first()
        assert user is not None
        assert user.balance == 100.0
    finally:
        session.close()


