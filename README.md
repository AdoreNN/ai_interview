# Grillo

Полноценный сервис подготовки к собеседованиям: адаптивный web-интерфейс, авторизация, постоянные интервью-сессии, разбор PDF-резюме и многоэтапное интервью с HR-, technical- и manager-агентами.

## Архитектура

- `frontend` (`http://localhost:3000`) — React/Vite, адаптивный интерфейс и демо-режим;
- `backend` (`http://localhost:8000`) — FastAPI, JWT, управление сессиями, LangGraph-интервью;
- `resume-parser` (`http://localhost:8001`) — извлечение текста PDF, анализ резюме, GitHub lookup и генерация персональных вопросов;
- `db` — PostgreSQL 16;
- таблица `sessions` хранит контекст резюме и состояние интервью между запросами.

## Быстрый запуск

```bash
cp .env.example .env
docker compose up --build
```

Откройте `http://localhost:3000`. По умолчанию `LLM_MODE=stub`: весь сценарий работает локально без внешнего ключа. Интерфейс также содержит демо-режим, который можно посмотреть без регистрации. Swagger backend доступен на `http://localhost:8000/docs`, parser — на `http://localhost:8001/docs`.

Для реального GigaChat укажите в `.env`:

```dotenv
LLM_MODE=gigachat
GIGACHAT_CREDENTIALS=<новый credential>
```

Не используйте credential, ранее попавший в ветку `pdf_parser_agent`: его необходимо отозвать. Настоящий `.env` не должен попадать в Git.

Остановка без удаления данных:

```bash
docker compose down
```

## API

| Метод и путь | Авторизация | Назначение |
|---|---|---|
| `GET /health` | Нет | Готовность backend и БД |
| `POST /api/v1/auth/sign-up` | Нет | Регистрация |
| `POST /api/v1/auth/sign-in` | Нет | Bearer access token |
| `POST /api/v1/sessions` | Bearer | Создать сессию |
| `GET /api/v1/sessions` | Bearer | Список своих сессий |
| `GET /api/v1/sessions/{session_id}` | Bearer | Получить свою сессию |
| `POST /api/v1/sessions/{session_id}/resume` | Bearer, multipart | Разобрать и сохранить PDF-резюме |
| `GET /api/v1/sessions/{session_id}/interview` | Bearer | Возобновить интервью и получить историю диалога |
| `POST /api/v1/sessions/{session_id}/interview/start` | Bearer | Начать интервью |
| `POST /api/v1/sessions/{session_id}/interview/answer` | Bearer | Отправить ответ и получить следующий вопрос/итог |

Создание сессии:

```json
{
  "title": "Python Junior",
  "target_position": "Python developer",
  "experience_level": "junior"
}
```

Ответ кандидата:

```json
{"answer": "На проекте я измерил проблему и изменил план выполнения."}
```

Допустимые уровни: `intern`, `junior`, `middle`, `senior`. Все операции с сессией проверяют владельца. Повторный старт и ответ до старта или после завершения возвращают `409`.

## Конфигурация

| Переменная | Назначение |
|---|---|
| `DATABASE_URL`, `POSTGRES_*` | Подключение и контейнер PostgreSQL |
| `JWT_SECRET`, `JWT_ALGORITHM` | Подпись access-токенов |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена |
| `ALLOWED_ORIGINS` | CORS origins через запятую |
| `LLM_MODE` | `stub` для автономного запуска или `gigachat` |
| `GIGACHAT_*` | Credential, scope, model и SSL-настройка GigaChat |
| `GITHUB_TOKEN` | Необязательный токен для увеличения лимита GitHub API |
| `RESUME_PARSER_URL` | Внутренний URL parser-сервиса |
| `MAX_RESUME_BYTES`, `MAX_RESUME_CHARS` | Лимиты PDF и извлечённого текста |
| `INTERVIEW_*_QUESTIONS` | Количество вопросов каждого этапа |
| `FRONTEND_PORT`, `BACKEND_PORT`, `RESUME_PARSER_PORT` | Порты сервисов на хосте |

## Frontend

Для локальной разработки интерфейса:

```bash
cd frontend
npm install
npm run dev
```

Vite проксирует `/api` на backend по адресу `http://localhost:8000`. В production-контейнере это делает nginx.

## Локальная разработка

```bash
uv sync --locked
docker compose up -d --wait db
export APP_ENV=test
export DATABASE_URL=postgresql+psycopg://grillo:grillo@127.0.0.1:5432/grillo
export JWT_SECRET=test-secret-with-at-least-thirty-two-characters
export LLM_MODE=stub
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Parser отдельно:

```bash
uv run uvicorn pdf_parser_agent.app.main:app --port 8001 --reload
```

## Проверки

```bash
uv run pytest
sh scripts/verify_tests.sh
sh scripts/verify_migrations.sh
sh scripts/verify_stack.sh
uv run --no-sync python scripts/verify_source_hygiene.py
uv run --no-sync python scripts/verify_docs.py
```

`verify_stack.sh` собирает Compose, запускает три сервиса и проводит authenticated smoke flow до итогового feedback.

## Миграции

Backend автоматически выполняет `alembic upgrade head` при старте. Для новой миграции:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Доменная схема сохраняет две таблицы — `users` и `sessions`; `alembic_version` является служебной.
