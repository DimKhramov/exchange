from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from config import get_settings
from models import Base

settings = get_settings()

# Создаем синхронный движок для Flask
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ECHO
)

# Создаем асинхронный движок для FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///'),
    echo=settings.ECHO,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db

def init_db():
    Base.metadata.create_all(bind=engine)
