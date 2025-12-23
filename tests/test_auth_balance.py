from app.db.base import SessionLocal
from app.models.user import UserDB


def test_register_user_success(client):
    payload = {
        "name": "Test User",
        "email": "test_user_success@example.com",
        "password": "password123",
        "telegram_id": None,
    }

    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == payload["email"]
    assert data["balance"] == 0.0


def test_register_user_duplicate_email(client):
    payload = {
        "name": "Test User",
        "email": "test_user_duplicate@example.com",
        "password": "password123",
        "telegram_id": None,
    }

    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400
    body = r2.json()
    assert "detail" in body


def test_login_success(client):
    register_payload = {
        "name": "Login User",
        "email": "login_user@example.com",
        "password": "password123",
        "telegram_id": None,
    }
    r = client.post("/auth/register", json=register_payload)
    assert r.status_code == 201

    r = client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert r.status_code == 200
    token_data = r.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == register_payload["email"]


def test_login_wrong_password(client):
    payload = {
        "name": "Wrong Password User",
        "email": "wrong_password@example.com",
        "password": "correct_password",
        "telegram_id": None,
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201

    r = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": "incorrect_password"},
    )
    assert r.status_code == 401
    body = r.json()
    assert "Incorrect email or password" in body.get("detail", "")


def test_login_unknown_email(client):
    r = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "somepassword"},
    )
    assert r.status_code == 401
    body = r.json()
    assert "Incorrect email or password" in body.get("detail", "")


def test_get_balance_initial_zero(client):
    payload = {
        "name": "Balance User",
        "email": "balance_zero@example.com",
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

    r = client.get("/users/me/balance", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["balance"] == 0.0


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

    session = SessionLocal()
    try:
        user = session.query(UserDB).filter(UserDB.id == user_id).first()
        assert user is not None
        assert user.balance == 100.0
    finally:
        session.close()


def test_admin_deposit_negative_amount_returns_400(client):
    session = SessionLocal()
    try:
        user = UserDB(
            id="neg-amount-user-id",
            telegram_id=None,
            name="Negative Amount User",
            email="neg_amount_user@example.com",
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
        json={"amount": -10.0, "description": "Неверное пополнение"},
    )
    assert r.status_code == 400
    body = r.json()
    assert "Amount must be positive" in body.get("detail", "")


def test_non_admin_cannot_use_admin_deposit(client):
    payload = {
        "name": "Simple User",
        "email": "simple_user@example.com",
        "password": "password123",
        "telegram_id": None,
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201
    simple_user_id = r.json()["id"]

    r = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        f"/admin/users/{simple_user_id}/balance/deposit",
        headers=headers,
        json={"amount": 50.0, "description": "Пополнение"},
    )
    assert r.status_code == 403
    body = r.json()
    assert "Admin access required" in body.get("detail", "")


def test_balance_requires_auth(client):
    r = client.get("/users/me/balance")
    assert r.status_code in (401, 403)


def test_admin_transactions_requires_admin(client):
    payload = {
        "name": "Tx Non Admin",
        "email": "tx_non_admin@example.com",
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

    r = client.get("/admin/transactions", headers=headers)
    assert r.status_code == 403


def test_admin_transactions_success_with_limit(client):
    # создаём пользователя и несколько транзакций
    session = SessionLocal()
    try:
        user = UserDB(
            id="admin-tx-user-id",
            telegram_id=None,
            name="Admin Tx User",
            email="admin_tx_user@example.com",
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

    for _ in range(3):
        r = client.post(
            f"/admin/users/{user_id}/balance/deposit",
            headers=admin_headers,
            json={"amount": 10.0, "description": "Пополнение"},
        )
        assert r.status_code == 200

    r = client.get("/admin/transactions?limit=2", headers=admin_headers)
    assert r.status_code == 200
    txs = r.json()
    assert len(txs) == 2

