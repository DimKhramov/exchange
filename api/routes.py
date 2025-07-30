from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from database import get_db
from models import ExchangeRate, APIKey
from datetime import datetime, timedelta
import os

router = APIRouter()

# Проверка API ключа
async def verify_api_key(api_key: str, db: Session = Depends(get_db)):
    key = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not key or key.disabled:
        raise HTTPException(status_code=401, detail="Invalid or disabled API key")
    return key

@router.get("/rates", tags=["exchange_rates"])
async def get_exchange_rates(
    currency: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    api_key: str = None,
    db: Session = Depends(get_db)
):
    """Получение курсов валют"""
    await verify_api_key(api_key, db)
    
    query = db.query(ExchangeRate)
    
    if currency:
        query = query.filter(ExchangeRate.currency_code == currency.upper())
    
    if start_date:
        query = query.filter(ExchangeRate.date >= start_date)
    
    if end_date:
        query = query.filter(ExchangeRate.date <= end_date)
    
    rates = query.order_by(ExchangeRate.date.desc()).all()
    
    return [{
        "currency": rate.currency_code,
        "rate": rate.rate,
        "date": rate.date.isoformat(),
        "source": rate.source,
        "nominal": rate.nominal
    } for rate in rates]

@router.get("/convert", tags=["exchange_rates"])
async def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float,
    api_key: str = None,
    db: Session = Depends(get_db)
):
    """Конвертация валют"""
    await verify_api_key(api_key, db)
    
    # Получаем текущие курсы валют
    from_rate = db.query(ExchangeRate).filter(
        ExchangeRate.currency_code == from_currency.upper(),
        ExchangeRate.date >= datetime.now() - timedelta(days=1)
    ).order_by(ExchangeRate.date.desc()).first()
    
    to_rate = db.query(ExchangeRate).filter(
        ExchangeRate.currency_code == to_currency.upper(),
        ExchangeRate.date >= datetime.now() - timedelta(days=1)
    ).order_by(ExchangeRate.date.desc()).first()
    
    if not from_rate or not to_rate:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    # Нормализуем курсы на номинал
    from_rate_norm = from_rate.rate / from_rate.nominal
    to_rate_norm = to_rate.rate / to_rate.nominal
    
    result = amount * (from_rate_norm / to_rate_norm)
    
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "amount": amount,
        "result": round(result, 2),
        "rate_date": from_rate.date.isoformat()
    }
