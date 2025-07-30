import urllib.request
from xml.etree import ElementTree
from datetime import datetime
import sys
from typing import Optional, List, Dict

def fetch_currencies():
    """Получение списка всех валют"""
    try:
        url = 'https://www.cbr.ru/scripts/XML_daily.asp'
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
        
        root = ElementTree.fromstring(xml_data)
        currencies = []
        
        for valute in root.findall('Valute'):
            currencies.append({
                'code': valute.find('CharCode').text,
                'numeric_code': valute.find('NumCode').text,
                'name': valute.find('Name').text,
                'nominal': int(valute.find('Nominal').text),
                'rate': float(valute.find('Value').text.replace(',', '.')),
                'date': datetime.now().strftime('%Y-%m-%d')
            })
        
        return currencies
        
    except Exception as e:
        print(f"Ошибка при получении валют: {str(e)}")
        return []

def format_currency(currency: dict) -> str:
    """Форматирование информации о валюте"""
    return f"{currency['code']} ({currency['numeric_code']}): {currency['name']} - {currency['rate']:.2f} руб. за {currency['nominal']} единиц"

def get_currency_by_code(currencies: list, code: str) -> Optional[dict]:
    """Получение валюты по коду"""
    return next((c for c in currencies if c['code'] == code.upper()), None)

def get_top_currencies(currencies: list, n: int = 5, reverse: bool = False) -> list:
    """Получение топ N валют по курсу"""
    sorted_currencies = sorted(
        currencies,
        key=lambda x: x['rate'] / x['nominal'],
        reverse=not reverse
    )
    return sorted_currencies[:n]

def convert_currency(currencies: list, from_currency: str, to_currency: str, amount: float) -> float:
    """Конвертация между валютами"""
    from_rate = get_currency_by_code(currencies, from_currency)
    to_rate = get_currency_by_code(currencies, to_currency)
    
    if not from_rate or not to_rate:
        return 0
        
    # Нормализуем курсы на номинал
    from_rate_norm = from_rate['rate'] / from_rate['nominal']
    to_rate_norm = to_rate['rate'] / to_rate['nominal']
    
    return amount * (from_rate_norm / to_rate_norm)

def get_currency_by_name(currencies: list, name: str) -> Optional[dict]:
    """Поиск валюты по части названия"""
    return next((c for c in currencies 
                if name.lower() in c['name'].lower()), None)

def get_currency_by_numeric_code(currencies: list, code: str) -> Optional[dict]:
    """Поиск валюты по числовому коду"""
    return next((c for c in currencies 
                if c['numeric_code'] == code), None)

def main():
    print("Загрузка данных о валютах...")
    currencies = fetch_currencies()
    
    if not currencies:
        print("Не удалось загрузить данные о валютах")
        return
    
    while True:
        print("\nВыберите действие:")
        print("1. Показать все валюты")
        print("2. Найти валюту по коду")
        print("3. Найти валюту по названию")
        print("4. Найти валюту по числовому коду")
        print("5. Показать топ валют")
        print("6. Конвертация валют")
        print("7. Выйти")
        
        choice = input("\nВаш выбор (1-7): ")
        
        if choice == '1':
            print("\nВсе валюты:")
            for currency in currencies:
                print(format_currency(currency))
                
        elif choice == '2':
            code = input("Введите код валюты (например, USD): ").upper()
            currency = get_currency_by_code(currencies, code)
            if currency:
                print(f"\nНайдена валюта:")
                print(format_currency(currency))
            else:
                print(f"Валюта с кодом {code} не найдена")
                
        elif choice == '3':
            name = input("Введите часть названия валюты: ")
            currency = get_currency_by_name(currencies, name)
            if currency:
                print(f"\nНайдена валюта:")
                print(format_currency(currency))
            else:
                print(f"Валюта с названием '{name}' не найдена")
                
        elif choice == '4':
            code = input("Введите числовой код валюты (например, 840): ")
            currency = get_currency_by_numeric_code(currencies, code)
            if currency:
                print(f"\nНайдена валюта:")
                print(format_currency(currency))
            else:
                print(f"Валюта с числовым кодом {code} не найдена")
                
        elif choice == '5':
            n = input("Сколько валют показать? (например, 5): ")
            try:
                n = int(n)
                print("\nТоп валют по курсу:")
                for currency in get_top_currencies(currencies, n):
                    print(format_currency(currency))
                print("\nТоп валют по курсу (самые дешевые):")
                for currency in get_top_currencies(currencies, n, reverse=True):
                    print(format_currency(currency))
            except ValueError:
                print("Введите число")
                
        elif choice == '6':
            from_code = input("Введите код исходной валюты (например, USD): ").upper()
            to_code = input("Введите код целевой валюты (например, EUR): ").upper()
            try:
                amount = float(input("Введите сумму: "))
                result = convert_currency(currencies, from_code, to_code, amount)
                print(f"{amount} {from_code} = {result:.2f} {to_code}")
            except ValueError:
                print("Введите числовое значение")
            except Exception as e:
                print(f"Ошибка конвертации: {str(e)}")
                
        elif choice == '7':
            print("До свидания!")
            break
            
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
