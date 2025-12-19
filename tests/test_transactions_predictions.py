from app.db.base import SessionLocal
from app.models.transaction import TransactionDB
from app.models.user import UserDB
from app.rabbitmq.publisher import publisher
from app.repositories import deposit, withdraw


def login(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_prediction_withdraws_balance_and_creates_transaction(client, monkeypatch):
    session = SessionLocal()
    try:
        user = UserDB(
            id="pred-user-id",
            telegram_id=None,
            name="Predict User",
            email="predict_user@example.com",
            hashed_password="dummy",
            role="user",
            balance=50.0,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    finally:
        session.close()

    monkeypatch.setattr(publisher, "publish_task", lambda task: True)

    session = SessionLocal()
    try:
        user = session.query(UserDB).filter(UserDB.id == user_id).first()
        user.balance = 50.0
        session.commit()
    finally:
        session.close()

    from app.core.security import create_access_token

    user_token = create_access_token({"sub": user_id})
    user_headers = {"Authorization": f"Bearer {user_token}"}

    text = "Создай на завтра встречу под названием \"Крутая встреча\" на 15:00"
    r = client.post("/predict/text", headers=user_headers, json={"text": text})
    assert r.status_code == 200
    body = r.json()
    assert body["input_data"] == text
    assert body["output_data"] is None

    session = SessionLocal()
    try:
        user = session.query(UserDB).filter(UserDB.id == user_id).first()
        assert user.balance == 40.0

        txs = (
            session.query(TransactionDB)
            .filter(TransactionDB.user_id == user_id)
            .order_by(TransactionDB.created_at.desc())
            .all()
        )
        assert any(tx.type.value == "withdrawal" and tx.amount == 10.0 for tx in txs)
    finally:
        session.close()


def test_prediction_insufficient_balance(client, monkeypatch):
    session = SessionLocal()
    try:
        user = UserDB(
            id="pred-low-balance-id",
            telegram_id=None,
            name="Low Balance User",
            email="low_balance@example.com",
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

    monkeypatch.setattr(publisher, "publish_task", lambda task: True)

    from app.core.security import create_access_token

    user_token = create_access_token({"sub": user_id})
    user_headers = {"Authorization": f"Bearer {user_token}"}

    r = client.post("/predict/text", headers=user_headers, json={"text": "some text"})
    assert r.status_code == 400
    body = r.json()
    assert "Insufficient funds" in body.get("detail", "")


def test_prediction_history_returns_items(client, monkeypatch):
    session = SessionLocal()
    try:
        user = UserDB(
            id="pred-history-id",
            telegram_id=None,
            name="History User",
            email="history_user@example.com",
            hashed_password="dummy",
            role="user",
            balance=100.0,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    finally:
        session.close()

    monkeypatch.setattr(publisher, "publish_task", lambda task: True)

    from app.core.security import create_access_token

    user_token = create_access_token({"sub": user_id})
    user_headers = {"Authorization": f"Bearer {user_token}"}

    texts = [
        "Создай встречу 1",
        "Создай встречу 2",
    ]
    for t in texts:
        r = client.post("/predict/text", headers=user_headers, json={"text": t})
        assert r.status_code == 200

    r = client.get("/users/me/predictions", headers=user_headers)
    assert r.status_code == 200
    preds = r.json()
    assert len(preds) >= 2
    input_texts = [p["input_data"] for p in preds]
    assert any(t in input_texts for t in texts)


def test_transactions_history_after_deposit_and_withdraw(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Tx User",
            "email": "tx_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201
    user_data = r.json()
    user_id = user_data["id"]

    session = SessionLocal()
    try:
        deposit(db=session, user_id=user_id, amount=100.0, description="Initial deposit")
        withdraw(db=session, user_id=user_id, amount=30.0, description="Spend credits")
    finally:
        session.close()

    token = login(client, "tx_user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/users/me/transactions", headers=headers)
    assert r.status_code == 200
    txs = r.json()
    assert len(txs) >= 2
    types = [tx["type"] for tx in txs]
    amounts = [tx["amount"] for tx in txs]
    assert "deposit" in types
    assert "withdrawal" in types
    assert 100.0 in amounts
    assert 30.0 in amounts


def test_transactions_history_respects_limit(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Tx Limit User",
            "email": "tx_limit_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201
    user_id = r.json()["id"]

    session = SessionLocal()
    try:
        for _ in range(5):
            deposit(db=session, user_id=user_id, amount=10.0, description="Deposit")
    finally:
        session.close()

    token = login(client, "tx_limit_user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/users/me/transactions?limit=3", headers=headers)
    assert r.status_code == 200
    txs = r.json()
    assert len(txs) == 3


def test_predictions_history_respects_limit(client, monkeypatch):
    session = SessionLocal()
    try:
        user = UserDB(
            id="pred-limit-id",
            telegram_id=None,
            name="Pred Limit User",
            email="pred_limit_user@example.com",
            hashed_password="dummy",
            role="user",
            balance=200.0,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    finally:
        session.close()

    monkeypatch.setattr(publisher, "publish_task", lambda task: True)

    from app.core.security import create_access_token

    user_token = create_access_token({"sub": user_id})
    headers = {"Authorization": f"Bearer {user_token}"}

    for i in range(5):
        r = client.post(
            "/predict/text",
            headers=headers,
            json={"text": f"Текст {i}"},
        )
        assert r.status_code == 200

    r = client.get("/users/me/predictions?limit=2", headers=headers)
    assert r.status_code == 200
    preds = r.json()
    assert len(preds) == 2


def test_predictions_history_empty(client):
    session = SessionLocal()
    try:
        user = UserDB(
            id="pred-empty-id",
            telegram_id=None,
            name="Pred Empty User",
            email="pred_empty_user@example.com",
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

    from app.core.security import create_access_token

    user_token = create_access_token({"sub": user_id})
    headers = {"Authorization": f"Bearer {user_token}"}

    r = client.get("/users/me/predictions", headers=headers)
    assert r.status_code == 200
    preds = r.json()
    assert preds == []


def test_transactions_history_empty(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Tx Empty User",
            "email": "tx_empty_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201

    token = login(client, "tx_empty_user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/users/me/transactions", headers=headers)
    assert r.status_code == 200
    txs = r.json()
    assert txs == []


def test_prediction_queue_publish_failure_returns_500(client, monkeypatch):
    session = SessionLocal()
    try:
        user = UserDB(
            id="pred-queue-fail-id",
            telegram_id=None,
            name="Queue Fail User",
            email="queue_fail_user@example.com",
            hashed_password="dummy",
            role="user",
            balance=50.0,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    finally:
        session.close()

    monkeypatch.setattr(publisher, "publish_task", lambda task: False)

    from app.core.security import create_access_token

    user_token = create_access_token({"sub": user_id})
    headers = {"Authorization": f"Bearer {user_token}"}

    r = client.post(
        "/predict/text",
        headers=headers,
        json={"text": "some text"},
    )
    assert r.status_code == 500


