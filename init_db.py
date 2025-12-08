from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from db_models import UserDB
from repositories import create_user


def init_demo_data(db: Session) -> None:
    if db.query(UserDB).count() > 0:
        return

    admin = create_user(
        db=db,
        telegram_id="1000",
        name="Admin",
        email="admin@example.com",
        role="admin",
        initial_balance=1000.0,
    )

    user = create_user(
        db=db,
        telegram_id="2000",
        name="Demo User",
        email="user@example.com",
        role="user",
        initial_balance=100.0,
    )

    print("Created admin:", admin.id)
    print("Created demo user:", user.id)


def main() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        init_demo_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()


