from db import Base, engine, SessionLocal
from db_models import UserDB
from repositories import (
    create_user,
    deposit,
    withdraw,
    get_transactions,
    get_user_balance,
)


def run_scenario() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        user = create_user(
            db=db,
            telegram_id="3000",
            name="Scenario User",
            email="scenario@example.com",
            role="user",
            initial_balance=0.0,
        )
        print("User created:", user.id)

        tx1 = deposit(db, user_id=user.id, amount=200.0, description="Первое пополнение")
        print("Deposit:", tx1.amount, "balance_after:", tx1.balance_after)

        tx2 = withdraw(db, user_id=user.id, amount=50.0, description="Покупка подписки")
        print("Withdraw:", tx2.amount, "balance_after:", tx2.balance_after)

        balance = get_user_balance(db, user_id=user.id)
        print("Current balance:", balance)

        history = get_transactions(db, user_id=user.id, limit=10)
        print("Last transactions:")
        for tx in history:
            print(
                f"- {tx.created_at} {tx.type.value} {tx.amount} "
                f"(balance_after={tx.balance_after})"
            )
    finally:
        db.close()


if __name__ == "__main__":
    run_scenario()


