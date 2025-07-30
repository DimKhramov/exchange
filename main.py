from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from config import get_settings
from models import User as UserModel
from database import get_db, init_db
from schemas import User, UserInDB, Token, TokenData, ExchangeRateResponse
import asyncio
import httpx
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

settings = get_settings()

# Инициализация базы данных
init_db()
db_dependency = Depends(get_db)

# Настройка шаблонов и статических файлов
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Настройки безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> Optional[UserInDB]:
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user:
        return UserInDB(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            api_key=user.api_key,
            disabled=user.disabled
        )
    return None

def authenticate_user(username: str, password: str, db: Session) -> Optional[UserInDB]:
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.external_api_key, algorithm="HS256")
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = db_dependency
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.external_api_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

# API endpoints
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/rates")
async def rates(request: Request, current_user: UserInDB = Depends(get_current_user)):
    return templates.TemplateResponse("rates.html", {"request": request})

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

@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = db_dependency,
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

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
