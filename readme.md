# 🚀 FastAPI Проект

Этот проект — учебное веб-приложение на FastAPI с PostgreSQL, Redis и SQLAlchemy.

## 📦 Стек технологий
- **FastAPI** — быстрый веб-фреймворк
- **PostgreSQL** — реляционная база данных
- **Redis** — хранение сессий
- **SQLAlchemy** — ORM для работы с базой данных  (асинхронное подключение через asyncpg)
- **Docker** — контейнеризация

## ⚙️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/wsdm777/python-fastapi.git
cd python-fastapi
```

### 2. Создание `.env` файла
Создай `.env` файл в корне проекта и добавь в него:
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME="dbname"
DB_USER="pguser"
DB_PASS="qwerty"
SUPERUSER_EMAIL="root@example.com"  # Почта автогенерируемого пользователя в БД
SUPERUSER_PASSWORD="root"
REDIS_HOST=localhost
REDIS_PORT=6379
UVICORN_WORKERS=1  # Количество воркеров Uvicorn
```

### 3. Запуск с Docker
```bash
docker-compose up --build
```

## 📁 Структура проекта
```
python-fastapi/
 ├── src/            # Исходный код приложения
 │   ├── auth/       # Аутентификация и авторизация
 │   │   ├── router.py
 │   │   ├── schemas.py
 │   ├── position/   # Логика позиций
 │   │   ├── router.py
 │   │   ├── schemas.py
 │   ├── user/       # Логика пользователей
 │   │   ├── router.py
 │   │   ├── schemas.py
 │   ├── vacation/   # Логика отпусков
 │   │   ├── router.py
 │   │   ├── schemas.py
 │   ├── services/   # Redis
 │   │   ├── redis.py
 │   ├── utils/      # Утилиты
 │   │   ├── logger.py
 │   │   ├── create_superuser.py
 │   ├── database.py     # Подключение к БД
 │   ├── databasemodels.py # Определение моделей SQLAlchemy
 │   ├── main.py         # Главный файл FastAPI
 │   ├── config.py       # Конфигурация проекта
 ├── alembic/         # Миграции Alembic
 ├── tests/           # Тесты
 ├── alembic.ini      # Конфигурация Alembic
 ├── docker-compose.yml  # Конфигурация Docker Compose
 ├── Dockerfile       # Конфигурация Docker
 ├── pytest.ini       # Конфигурация Pytest
 ├── redis.ini        # Конфигурация Redis
 ├── requirements.txt # Список зависимостей
 ├── .gitignore       # Игнорируемые файлы в Git
 ├── screenshots      # Скриншоты Swagger Ui
```

## 📖 Документация API

Swagger UI доступен по адресу:

```
http://localhost:8080/docs
```

ReDoc доступен по адресу:

```
http://localhost:8080/redoc
```

### Swagger UI

![Swagger UI](screenshots/swagger_ui.png)


## ✅ Тестирование
```bash
pytest
```

