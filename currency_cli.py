from currency_utils import CurrencyManager
from typing import Optional
import sys

def format_currency(currency: Dict) -> str:
    """Форматирование информации о валюте"""
    return f"{currency['code']} ({currency['numeric_code']}): {currency['name']} - {currency['rate']:.2f} руб. за {currency['nominal']} единиц"

def main():
    manager = CurrencyManager()
    print("Загрузка данных о валютах...")
    currencies = manager.fetch_currencies()
    
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
            currency = manager.get_currency_by_code(code)
            if currency:
                print(f"\nНайдена валюта:")
                print(format_currency(currency))
            else:
                print(f"Валюта с кодом {code} не найдена")
                
        elif choice == '3':
            name = input("Введите часть названия валюты: ")
            currency = manager.get_currency_by_name(name)
            if currency:
                print(f"\nНайдена валюта:")
                print(format_currency(currency))
            else:
                print(f"Валюта с названием '{name}' не найдена")
                
        elif choice == '4':
            code = input("Введите числовой код валюты (например, 840): ")
            currency = manager.get_currency_by_numeric_code(code)
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
                for currency in manager.get_top_currencies(n):
                    print(format_currency(currency))
                print("\nТоп валют по курсу (самые дешевые):")
                for currency in manager.get_top_currencies(n, reverse=True):
                    print(format_currency(currency))
            except ValueError:
                print("Введите число")
                
        elif choice == '6':
            from_code = input("Введите код исходной валюты (например, USD): ").upper()
            to_code = input("Введите код целевой валюты (например, EUR): ").upper()
            try:
                amount = float(input("Введите сумму: "))
                result = manager.convert_currency(from_code, to_code, amount)
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
