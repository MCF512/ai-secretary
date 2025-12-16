from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.base import Base, engine, SessionLocal
from app.api import auth, balance, transactions, predictions, admin, calendar
from app.repositories import create_user
from app.rabbitmq.publisher import publisher


def init_demo_data() -> None:
    """Инициализирует демо-данные в БД"""
    db = SessionLocal()
    try:
        from app.models.user import UserDB
        if db.query(UserDB).count() > 0:
            return

        admin = create_user(
            db=db,
            telegram_id="1000",
            name="Admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
            initial_balance=1000.0,
        )

        user = create_user(
            db=db,
            telegram_id="2000",
            name="Demo User",
            email="user@example.com",
            password="user123",
            role="user",
            initial_balance=100.0,
        )

        print("Created admin:", admin.id)
        print("Created demo user:", user.id)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    init_demo_data()
    try:
        publisher._connect()
    except Exception as e:
        print(f"Warning: Could not connect to RabbitMQ at startup: {e}")
    yield
    publisher.close()


app = FastAPI(
    title="AI Secretary API",
    version="1.0.0",
    lifespan=lifespan,
    tags_metadata=[
        {
            "name": "health",
            "description": "Проверка работоспособности API",
        },
        {
            "name": "auth",
            "description": "Регистрация и авторизация пользователей",
        },
        {
            "name": "balance",
            "description": "Управление балансом пользователя",
        },
        {
            "name": "transactions",
            "description": "История транзакций",
        },
        {
            "name": "predictions",
            "description": "Работа с ML-предсказаниями",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(balance.router)
app.include_router(transactions.router)
app.include_router(predictions.router)
app.include_router(admin.router)
app.include_router(calendar.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/", tags=["health"], summary="Главная")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login.html", tags=["health"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register.html", tags=["health"])
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard.html", tags=["health"])
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/admin.html", tags=["health"])
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/calendar.html", tags=["health"])
async def calendar_page(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})


@app.get("/health", tags=["health"], summary="Проверка работоспособности API")
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

