import urllib.request
from xml.etree import ElementTree
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='currency_check.log'
)
logger = logging.getLogger(__name__)

def get_all_currencies():
    """Получение списка всех валют от ЦБ РФ"""
    try:
        # Получаем XML данные
        url = 'https://www.cbr.ru/scripts/XML_daily.asp'
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
        
        # Парсим XML
        root = ElementTree.fromstring(xml_data)
        
        # Создаем список валют
        currencies = []
        for valute in root.findall('Valute'):
            currencies.append({
                'code': valute.find('CharCode').text,
                'numeric_code': valute.find('NumCode').text,
                'name': valute.find('Name').text,
                'nominal': int(valute.find('Nominal').text),
                'rate': float(valute.find('Value').text.replace(',', '.'))
            })
        
        return currencies
    except Exception as e:
        logger.error(f"Ошибка при получении списка валют: {str(e)}")
        return []

def main():
    """Основная функция"""
    currencies = get_all_currencies()
    
    if currencies:
        logger.info(f"Найдено {len(currencies)} валют")
        
        # Группируем валюты по категориям
        major_currencies = []
        other_currencies = []
        
        for currency in currencies:
            if currency['code'] in ['USD', 'EUR', 'GBP', 'CNY', 'JPY']:
                major_currencies.append(currency)
            else:
                other_currencies.append(currency)
        
        # Выводим основные валюты
        print("\nОсновные валюты:")
        for currency in major_currencies:
            print(f"{currency['code']} ({currency['numeric_code']}): {currency['name']} - {currency['rate']} руб. за {currency['nominal']} единиц")
        
        # Выводим остальные валюты
        print("\nДругие валюты:")
        for currency in other_currencies:
            print(f"{currency['code']} ({currency['numeric_code']}): {currency['name']} - {currency['rate']} руб. за {currency['nominal']} единиц")
        
        print(f"\nВсего валют: {len(currencies)}")
        print(f"Основных валют: {len(major_currencies)}")
        print(f"Других валют: {len(other_currencies)}")
    else:
        logger.error("Не удалось получить список валют")

if __name__ == "__main__":
    main()
