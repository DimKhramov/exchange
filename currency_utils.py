import requests
from xml.etree import ElementTree
from datetime import datetime
import logging
from typing import List, Dict, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='currency_utils.log'
)
logger = logging.getLogger(__name__)

class CurrencyManager:
    def __init__(self):
        self.currencies = []
        
    def fetch_currencies(self) -> List[Dict]:
        """Получение списка всех валют"""
        try:
            url = 'https://www.cbr.ru/scripts/XML_daily.asp'
            with requests.get(url) as response:
                response.raise_for_status()
                xml_data = response.text
            
            root = ElementTree.fromstring(xml_data)
            self.currencies = []
            
            for valute in root.findall('Valute'):
                self.currencies.append({
                    'code': valute.find('CharCode').text,
                    'numeric_code': valute.find('NumCode').text,
                    'name': valute.find('Name').text,
                    'nominal': int(valute.find('Nominal').text),
                    'rate': float(valute.find('Value').text.replace(',', '.')),
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            
            return self.currencies
            
        except Exception as e:
            logger.error(f"Ошибка при получении валют: {str(e)}")
            return []
    
    def get_currency_by_code(self, code: str) -> Optional[Dict]:
        """Получение валюты по коду"""
        return next((c for c in self.currencies if c['code'] == code.upper()), None)
    
    def get_top_currencies(self, n: int = 5, reverse: bool = False) -> List[Dict]:
        """Получение топ N валют по курсу"""
        sorted_currencies = sorted(
            self.currencies,
            key=lambda x: x['rate'] / x['nominal'],
            reverse=not reverse
        )
        return sorted_currencies[:n]
    
    def convert_currency(self, from_currency: str, to_currency: str, amount: float) -> float:
        """Конвертация между валютами"""
        from_rate = self.get_currency_by_code(from_currency)
        to_rate = self.get_currency_by_code(to_currency)
        
        if not from_rate or not to_rate:
            return 0
            
        # Нормализуем курсы на номинал
        from_rate_norm = from_rate['rate'] / from_rate['nominal']
        to_rate_norm = to_rate['rate'] / to_rate['nominal']
        
        return amount * (from_rate_norm / to_rate_norm)
    
    def get_currency_by_name(self, name: str) -> Optional[Dict]:
        """Поиск валюты по части названия"""
        return next((c for c in self.currencies 
                    if name.lower() in c['name'].lower()), None)
    
    def get_currency_by_numeric_code(self, code: str) -> Optional[Dict]:
        """Поиск валюты по числовому коду"""
        return next((c for c in self.currencies 
                    if c['numeric_code'] == code), None)
