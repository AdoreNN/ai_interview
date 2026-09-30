# pdf_parser_agent

Самостоятельный агент, без зависимостей от остального репозитория (свой
`requirements.txt`, свой `Dockerfile`, свои креды). Три скилла:

1. **`read_resume`** (`app/skills/read_resume.py`) — читает PDF, извлекает
   текст (`pypdf`), одним вызовом LLM разбирает его в структурированные данные:
   технологии, оценка опыта по ним, предполагаемая позиция и уровень.
2. **`github_lookup`** (`app/skills/github_lookup.py`) — ищет в тексте резюме
   ссылку вида `github.com/<username>` и, если находит, тянет публичный
   профиль и топ-репозитории (по звёздам, без форков) через GitHub REST API.
   Без LLM, обычный HTTP-запрос. Если ссылки нет, профиль не найден или
   GitHub недоступен — просто `null`, это не ошибка.
3. **`generate_questions`** (`app/skills/generate_questions.py`) — вторым
   вызовом LLM генерирует вопросы под это резюме (+ GitHub-контекст, если он
   есть), каждый с меткой, какому агенту-собеседователю (`tech`/`hr`/`manager`)
   он адресован.

Эндпоинт `/v1/parse` вызывает эти три скилла по очереди и отдаёт общий
результат — сам агент не решает, что делать с вопросами дальше, этим
занимается оркестратор.

## Запуск локально

```bash
cd pdf_parser_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # вписать GIGACHAT_CREDENTIALS
uvicorn app.main:app --reload --port 8000
```

Проверка, что поднялся:

```bash
curl localhost:8000/health
```

## Запуск в Docker

```bash
docker build -t pdf_parser_agent .
docker run --rm -p 8000:8000 --env-file .env pdf_parser_agent
```

Контейнер слушает `0.0.0.0:8000` (см. `Dockerfile`), наружу пробрасывается
через `-p`. Креды передаются через `--env-file`, в образ не запекаются.

## Переменные окружения (`.env`)

| Переменная            | Обязательна | По умолчанию        | Назначение                                   |
|------------------------|:-----------:|----------------------|-----------------------------------------------|
| `GIGACHAT_CREDENTIALS`| да          | —                    | ключ авторизации GigaChat                     |
| `GIGACHAT_SCOPE`       | нет         | `GIGACHAT_API_PERS`  | scope доступа GigaChat                        |
| `GIGACHAT_MODEL`       | нет         | `GigaChat-2-Pro`     | модель                                        |
| `GIGACHAT_VERIFY_SSL`  | нет         | `false`              | проверка SSL-сертификата GigaChat             |
| `MAX_RESUME_CHARS`     | нет         | `12000`              | обрезка текста резюме перед отправкой в LLM   |
| `MAX_QUESTIONS`        | нет         | `8`                  | верхняя граница числа генерируемых вопросов   |
| `GITHUB_TOKEN`         | нет         | —                    | поднимает лимит GitHub API с 60 до 5000 запросов/час |

Без `GIGACHAT_CREDENTIALS` агент поднимется (health отвечает), но любой
запрос к `/v1/parse` упадёт при первом же обращении к LLM. Без `GITHUB_TOKEN`
skill `github_lookup` тоже работает, просто на публичном (небольшом) лимите
GitHub API — общем на весь исходящий IP, не только на этот агент.

## API-контракт (для оркестратора)

### `GET /health`

```json
{ "status": "ok", "agent": "pdf_parser_agent" }
```

Без внешних вызовов (LLM не трогает) — годится для Docker `HEALTHCHECK` /
readiness-проверки оркестратора.

### `POST /v1/parse`

**Входящий формат — не JSON.** Тело запроса — `multipart/form-data` с одним
файлом (PDF) в поле **`file`**; JSON-body этот эндпоинт не принимает.

```bash
curl -X POST localhost:8000/v1/parse -F "file=@resume.pdf"
```

Тело ответа (`200 OK`):

```json
{
  "parsed_resume": {
    "resume_topics": ["Python", "PostgreSQL", "Docker"],
    "resume_experience": { "Python": 3 },
    "target_position": "Python backend developer",
    "experience_level": "middle"
  },
  "github_profile": {
    "username": "octocat",
    "name": "The Octocat",
    "bio": null,
    "public_repos": 8,
    "profile_url": "https://github.com/octocat",
    "top_repos": [
      {
        "name": "Spoon-Knife",
        "description": "This repo is for demonstration purposes only.",
        "language": "HTML",
        "stars": 14066,
        "url": "https://github.com/octocat/Spoon-Knife"
      }
    ]
  },
  "questions": [
    {
      "topic": "PostgreSQL",
      "question": "В резюме указана разработка SQL-процедур для иерархического сбора метрик. Расскажите подробнее про этот кейс.",
      "target_agent": "tech"
    }
  ]
}
```

Поля `parsed_resume`:

| Поле                | Тип               | Может быть пустым/null | Комментарий                                                       |
|---------------------|-------------------|:-----------------------:|---------------------------------------------------------------------|
| `resume_topics`     | `string[]`        | да, `[]`                | технологии/навыки, упомянутые в резюме                              |
| `resume_experience` | `object<str,int>` | да, `{}`                | годы опыта по теме из `resume_topics`; заполняется **только** если модель может это вывести из текста — на практике часто пустой, это нормально, не баг |
| `target_position`   | `string \| null`  | да                       | предполагаемая позиция кандидата                                    |
| `experience_level`  | `string \| null`  | да                       | одно из `intern / junior / middle / senior`                         |

`github_profile` — `null`, если в резюме нет ссылки на GitHub-профиль, юзер
не найден или GitHub был недоступен. Если не `null`:

| Поле           | Тип            | Комментарий                                             |
|-----------------|----------------|------------------------------------------------------------|
| `username`      | `string`       | из ссылки в резюме                                        |
| `name`, `bio`   | `string\|null` | из публичного профиля GitHub                               |
| `public_repos`  | `int`          | всего публичных репозиториев у пользователя                |
| `profile_url`   | `string`       | ссылка на профиль                                          |
| `top_repos`     | `array`        | до 5 репозиториев (не форки), отсортированы по звёздам; каждый — `{name, description, language, stars, url}` |

Поля одного элемента `questions[]`:

| Поле           | Тип      | Комментарий                                                        |
|-----------------|----------|----------------------------------------------------------------------|
| `topic`         | `string` | тема вопроса (обычно конкретная технология/проект из резюме)        |
| `question`      | `string` | готовый текст вопроса кандидату                                     |
| `target_agent`  | `string` | `tech` / `hr` / `manager` — какому агенту-собеседователю передать   |

`questions` может быть пустым списком — это ожидаемый результат для
нечитаемого/почти пустого резюме, агент не пытается придумать вопросы "на
пустом месте" (см. промпты в `app/skills/*.py`).

### JSON Schema ответа (`200 OK`)

Сгенерирована из реальных pydantic-моделей (`ParseResumeResponse.model_json_schema()`
в `app/schemas.py`) — если модели поменяются, эту схему нужно перегенерировать
тем же способом, руками не править.

```json
{
  "$defs": {
    "GeneratedQuestion": {
      "description": "Один вопрос из skill 2 (генерация вопросов), для последующей раздачи агентам-собеседователям оркестратором.",
      "properties": {
        "topic": { "type": "string", "description": "Тема вопроса, например конкретная технология из резюме" },
        "question": { "type": "string", "description": "Текст вопроса кандидату" },
        "target_agent": { "type": "string", "enum": ["tech", "hr", "manager"], "description": "Какому агенту-собеседователю передать этот вопрос" }
      },
      "required": ["topic", "question", "target_agent"],
      "type": "object"
    },
    "GithubRepo": {
      "description": "Один репозиторий кандидата (не форк), из skill 3 (github_lookup).",
      "properties": {
        "name": { "type": "string" },
        "description": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
        "language": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
        "stars": { "type": "integer", "default": 0 },
        "url": { "type": "string" }
      },
      "required": ["name", "url"],
      "type": "object"
    },
    "GithubProfile": {
      "description": "Результат skill 3: публичный профиль GitHub, если ссылка нашлась в резюме.",
      "properties": {
        "username": { "type": "string" },
        "name": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
        "bio": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
        "public_repos": { "type": "integer", "default": 0 },
        "profile_url": { "type": "string" },
        "top_repos": { "type": "array", "items": { "$ref": "#/$defs/GithubRepo" } }
      },
      "required": ["username", "profile_url"],
      "type": "object"
    },
    "ParsedResume": {
      "description": "Результат skill 1 (чтение и разбор PDF).",
      "properties": {
        "resume_topics": { "type": "array", "items": { "type": "string" }, "description": "Технологии и навыки, упомянутые в резюме" },
        "resume_experience": { "type": "object", "additionalProperties": { "type": "integer" }, "description": "Опыт в годах по темам из resume_topics, если его можно оценить" },
        "target_position": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "description": "Позиция, на которую похоже претендует кандидат" },
        "experience_level": { "anyOf": [{ "type": "string", "enum": ["intern", "junior", "middle", "senior"] }, { "type": "null" }], "default": null, "description": "Оценка уровня кандидата по резюме" }
      },
      "required": ["resume_topics", "resume_experience"],
      "type": "object"
    }
  },
  "properties": {
    "parsed_resume": { "$ref": "#/$defs/ParsedResume" },
    "github_profile": { "anyOf": [{ "$ref": "#/$defs/GithubProfile" }, { "type": "null" }], "default": null },
    "questions": { "type": "array", "items": { "$ref": "#/$defs/GeneratedQuestion" } }
  },
  "required": ["parsed_resume", "questions"],
  "type": "object"
}
```

### Ошибки

| Код | Когда | Content-Type | Тело |
|-----|-------|--------------|------|
| `422` | PDF повреждён / не PDF / прочитался без текста (скан без OCR) | `application/json` | `{ "detail": "<человекочитаемая причина>" }` |
| `500` | Сбой при обращении к GigaChat (сеть, невалидные креды, рейт-лимит, невалидная схема и т.п.) | `text/plain` | **не JSON** — обычный текст `Internal Server Error`, без деталей |

Важно для парсинга на стороне оркестратора: `500` не гарантирует JSON-тело —
пытаться сделать `response.json()` на нём не стоит, только на `200`/`422`.
Оркестратору имеет смысл ретраить `500` с бэкоффом (может быть временный сбой
GigaChat), а `422` — не ретраить, это финальный вердикт по конкретному файлу.

### Тайминги

Один запрос — это **три последовательных шага**, не параллельных:
`read_resume` (LLM) → `github_lookup` (HTTP к GitHub, только если есть
ссылка) → `generate_questions` (LLM). Замерено на реальных резюме:
~8.4 секунды без GitHub-ссылки (два вызова LLM), ~11 секунд с ней (два LLM +
два запроса к GitHub API). Оркестратору не стоит держать запрос синхронно в
UI-потоке, лучше через очередь/фоновую задачу.

### Что ещё не сделано (учитывать при подключении оркестратора)

- Нет ограничения на размер загружаемого файла — стоит проверять размер до
  отправки сюда, либо добавить лимит здесь отдельным тикетом.
- Нет ретраев на сбой GigaChat внутри самого агента — ретраить снаружи.
- Нет аутентификации эндпоинта — предполагается, что агент живёт за
  внутренней сетью/оркестратором, не смотрит наружу напрямую.
- Каждый запрос независим, состояния между запросами агент не хранит.
- GitHub API без `GITHUB_TOKEN` ограничен 60 запросами/час **на исходящий
  IP** (не на агента) — при заметном трафике стоит завести токен.
- `github_lookup` берёт только первую ссылку вида `github.com/<username>` в
  тексте резюме; если там несколько разных профилей — остальные игнорируются.
