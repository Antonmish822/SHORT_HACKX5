# Smart Wall API — X5 Tech

API для регистрации, авторизации и учёта прогресса на умной стене.

## Описание

Это backend-приложение для интерактивной платформы "Умная стена X5 Tech", разработанной во время хакатона. Приложение предоставляет REST API для управления пользователями, заданиями и отслеживания прогресса участников.

Основные функции:

- Регистрация и аутентификация пользователей (через email или Telegram)
- Система баллов и уровней
- Создание и выполнение заданий различных типов
- Магазин призов
- Сбор информации о предпочтениях пользователей

## Технологии

- Python 3.8+
- FastAPI
- SQLAlchemy (ORM)
- SQLite (база данных)
- JWT (аутентификация)
- Pydantic (валидация данных)

## Зависимости

Для установки зависимостей используйте файл requirements.txt:
```bash
pip install -r requirements.txt
```

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Если файл базы данных smartwall.db уже находится в индексе Git, удалите его оттуда:
   ```bash
   git rm --cached HACK/smartwall.db
   ```

5. Перейдите в директорию HACK:
   ```bash
   cd HACK
   ```

6. Запустите приложение:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

7. API будет доступно по адресу: `http://localhost:8000`

## Документация API

После запуска приложения документация будет доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Тестирование API

Для тестирования API можно использовать Postman-коллекцию, которая находится в файле `HACK Smart Wall API.postman_collection.json`.

## Структура проекта

```
backend/
├── README.md                    # Этот файл
├── requirements.txt             # Файл зависимостей
└── HACK/                        # Основная директория приложения
    ├── main.py                  # Основной файл приложения
    ├── models.py                # Модели данных SQLAlchemy
    ├── schemas.py               # Pydantic схемы
    ├── auth.py                  # Модуль аутентификации
    ├── database.py              # Конфигурация базы данных
    ├── crud.py                  # Функции для работы с БД
    ├── smartwall.db             # Файл базы данных SQLite
    └── test.db                  # Тестовая база данных
```

## Основные эндпоинты

- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Вход в систему
- `GET /me` - Получение информации о пользователе
- `PUT /me/interests` - Обновление интересов пользователя
- `GET /quests/` - Получение списка заданий
- `POST /quests/{quest_id}/submit` - Отправка решения задания
- `POST /admin/quests` - Создание нового задания (админка)

## Лицензия

Проект разработан в рамках хакатона X5 Tech.