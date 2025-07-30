import logging
import sys
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from config import get_settings
from models import User as UserModel
from database import get_db, get_async_db, init_db
from schemas import User, UserInDB, Token, TokenData, ExchangeRateResponse
import asyncio
import httpx
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка приложения
settings = get_settings()

# Инициализация базы данных
init_db()
db_dependency = Depends(get_db)
async_db_dependency = Depends(get_async_db)

# Настройка шаблонов и статических файлов
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем роут для страницы регистрации
@app.get("/register")
async def register(request: Request):
    logger.info("Registration page requested")
    return templates.TemplateResponse("register.html", {"request": request})

# Добавляем роут для страницы с курсами валют
@app.get("/rates")
async def rates(request: Request, current_user: UserInDB = Depends(get_current_user)):
    logger.info("Rates page requested")
    return templates.TemplateResponse("rates.html", {"request": request})

# API endpoints
@app.post("/register")
async def register_user(
    username: str,
    email: str,
    password: str,
    full_name: str,
    db: Session = db_dependency
):
    existing_user = get_user(db, username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    user = UserModel(
        username=username,
        email=email,
        full_name=full_name,
        disabled=False,
        api_key=secrets.token_urlsafe(32)
    )
    user.hashed_password = get_password_hash(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User registered successfully"}

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = db_dependency,
) -> dict:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/latest/{base_currency}", response_model=ExchangeRateResponse)
async def get_latest_rates(
    base_currency: str,
    current_user: UserInDB = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        )
        response.raise_for_status()
        data = response.json()
        return ExchangeRateResponse(
            base_currency=base_currency,
            conversion_rates=data["rates"],
            time_last_update_utc=data["time_last_update_utc"],
            time_next_update_utc=data["time_next_update_utc"]
        )

if __name__ == "__main__":
    logger.info("Starting server...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import aiosqlite
        logger.info(f"FastAPI version: {fastapi.__version__}")
        logger.info(f"Uvicorn version: {uvicorn.__version__}")
        logger.info("All dependencies loaded successfully")
    except Exception as e:
        logger.error(f"Error loading dependencies: {e}")
        raise
    
    # Устанавливаем логирование для uvicorn
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройки сервера
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
    
    # Запуск сервера
    server = uvicorn.Server(config)
    logger.info(f"Starting server on http://{config.host}:{config.port}")
    server.run()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Настройки безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функции для аутентификации
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.username == username).first()

def authenticate_user(username: str, password: str, db: Session) -> Optional[UserInDB]:
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return UserInDB(**user.__dict__)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

# Функция для получения текущего пользователя
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return UserInDB(**user.__dict__)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"FastAPI version: {fastapi.__version__}")
    logger.info(f"Uvicorn version: {uvicorn.__version__}")
    
    # Проверяем, что все зависимости загружены
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import aiosqlite
        logger.info("All dependencies loaded successfully")
    except Exception as e:
        logger.error(f"Error loading dependencies: {e}")
        raise
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
