# Grillo backend

Базовый backend для сервиса подготовки к техническим собеседованиям. Текущая версия отвечает за регистрацию и вход пользователей, а также за создание и чтение принадлежащих им интервью-сессий. Диалог с LLM и итоговый feedback в этот change не входят.

## Стек

- Python 3.12 и FastAPI;
- SQLAlchemy 2 и PostgreSQL 16;
- Alembic для миграций;
- JWT access-токены и Argon2 для паролей;
- Docker Compose для локального запуска.

## Быстрый запуск

Создайте локальный файл конфигурации:

```bash
cp .env.example .env
```

Поменяйте `POSTGRES_PASSWORD` и `JWT_SECRET`, затем запустите сервисы:

```bash
docker compose up --build
```

Backend будет доступен на `http://localhost:8000`, документация OpenAPI — на `http://localhost:8000/docs`. При запуске контейнер backend автоматически выполняет `alembic upgrade head`.

Остановить сервисы без удаления данных:

```bash
docker compose down
```

Удалять volume с данными следует только осознанно:

```bash
docker compose down --volumes
```

## Переменные окружения

| Переменная | Назначение |
|---|---|
| `DATABASE_URL` | URL PostgreSQL для локальных команд вне Compose |
| `JWT_SECRET` | Секрет подписи JWT, минимум 32 символа |
| `JWT_ALGORITHM` | Алгоритм JWT, по умолчанию `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена |
| `ALLOWED_ORIGINS` | Разрешённые CORS origins через запятую |
| `POSTGRES_*` | Параметры контейнера PostgreSQL |
| `BACKEND_PORT` | Порт backend на хосте |

Настоящий `.env` не должен попадать в Git. `.env.example` содержит только шаблон.

## API

| Метод и путь | Авторизация | Назначение |
|---|---|---|
| `GET /health` | Нет | Проверить backend и соединение с БД |
| `POST /api/v1/auth/sign-up` | Нет | Зарегистрировать пользователя |
| `POST /api/v1/auth/sign-in` | Нет | Получить bearer access-токен |
| `POST /api/v1/sessions` | Bearer | Создать интервью-сессию |
| `GET /api/v1/sessions` | Bearer | Получить свои сессии |
| `GET /api/v1/sessions/{session_id}` | Bearer | Получить свою конкретную сессию |

Пример создания сессии:

```json
{
  "title": "Python Junior",
  "target_position": "Python developer",
  "experience_level": "junior"
}
```

Допустимые уровни: `intern`, `junior`, `middle`, `senior`.

## Локальная разработка

Установите [uv](https://docs.astral.sh/uv/) и синхронизируйте окружение по lock-файлу:

```bash
uv sync --locked
```

Поднимите PostgreSQL:

```bash
docker compose up -d --wait db
```

Экспортируйте `DATABASE_URL` и `JWT_SECRET` из `.env`, затем примените миграции:

```bash
uv run alembic upgrade head
```

Запуск backend без контейнера:

```bash
uv run uvicorn app.main:app --reload
```

Запуск тестов:

```bash
uv run pytest
```

Полные проверки проекта:

```bash
sh scripts/verify_tests.sh
sh scripts/verify_migrations.sh
sh scripts/verify_backend.sh
```

## Миграции

Новая миграция после изменения моделей:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Применение миграций:

```bash
uv run alembic upgrade head
```

Схема содержит две доменные таблицы: `users` и `sessions`. Таблица `alembic_version` является служебной.
