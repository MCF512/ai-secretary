from app.db.base import SessionLocal
from app.models.transaction import TransactionDB
from app.models.user import UserDB
from app.rabbitmq.publisher import publisher


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

    token = login(client, "admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200

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


