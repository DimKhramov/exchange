from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = False
    api_key: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ExchangeRateResponse(BaseModel):
    base_currency: str
    conversion_rates: Dict[str, float]
    time_last_update_utc: datetime
    time_next_update_utc: datetime
