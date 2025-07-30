# Currency Exchange API

API для получения курсов валют с веб-интерфейсом для продажи API ключей.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте виртуальное окружение (опционально):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Запуск

### API сервер

1. Перейдите в директорию API:
```bash
cd api
```

2. Запустите сервер:
```bash
python main.py
```

API будет доступен по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

### Веб-интерфейс

1. Перейдите в директорию веб-интерфейса:
```bash
cd web
```

2. Запустите Flask приложение:
```bash
python app.py
```

Веб-интерфейс будет доступен по адресу: http://localhost:5000

## Использование API

### Получение курсов валют
```
GET /api/rates
```

Параметры:
- `currency`: код валюты (например, USD)
- `start_date`: начальная дата
- `end_date`: конечная дата
- `api_key`: API ключ

### Конвертация валют
```
GET /api/convert
```

Параметры:
- `from_currency`: исходная валюта
- `to_currency`: целевая валюта
- `amount`: сумма для конвертации
- `api_key`: API ключ

## База данных

Используется SQLite. Таблицы создаются автоматически при первом запуске.

## Лицензия

MIT