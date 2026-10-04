# analyst_agent

Агент-аналитик для AI-собеседований. Когда интервью закончилось, он:

1. **пишет кандидату итоговый фидбек**: общее впечатление, сильные и слабые стороны, рекомендации;
2. **отвечает на вопросы кандидата** по результатам.


## Место в системе

```
резюме ──► парсер ──► оркестратор ──► агенты-интервьюеры (hr / tech / manager)
                          │                        │
                          │       итог интервью    │
                          ◄────────────────────────┘
                          │
                          ▼
                    analyst_agent  ──►  фидбек и ответы на вопросы ──► пользователь
```


## Как это работает

**Числа считает код, текст пишет модель.** Средние баллы и лучшие/худшие темы
считает обычный Python. LLM получает готовые числа и
оценки с обоснованиями интервьюеров и по ним пишет связный текст.

```
START ─► compute_stats ─┬─ режим "feedback" ─► write_feedback  ─► END
                        └─ режим "chat"     ─► answer_question ─► END
```

| Шаг | Что происходит |
|---|---|
| `compute_stats` | проверяет, что есть что анализировать, и считает `stats` (без LLM) |
| `write_feedback` | один вызов GigaChat со структурным ответом `Feedback`; невалидный ответ повторяется |
| `answer_question` | один вызов GigaChat: контекст интервью, выданный фидбек, история чата, вопрос |

## Локальный запуск

```bash
cd analyst_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env # впишите GIGACHAT_CREDENTIALS
uvicorn app.main:app --reload --port 8002
```

Проверка:

```bash
curl localhost:8002/health

curl -s -X POST localhost:8002/v1/feedback \
  -H "Content-Type: application/json" \
  -d @samples/sample_state.json | python3 -m json.tool --no-ensure-ascii
```


## API

### `GET /health`

Возвращает `{"status": "ok", "agent": "analyst_agent"}`.

### `POST /v1/feedback`: итоговый фидбек

**Вход.** JSON с итогами интервью. Поля повторяют `InterviewState` интервьюеров, поэтому итоговый
state можно отправить как есть: лишние поля (`hr_count`, `finished`, `final_feedback` и т.п.)
игнорируются.

| Поле | Тип | Описание |
|---|---|---|
| `messages` | `[{role, content}]` | диалог. `role: "user"` — кандидат, любая другая интервьюер |
| `evaluation_log` | `[{skill, score, reason}]` | оценки ответов. `skill` в формате `этап.тема` (`tech.async`), `score` 0–10, `reason` - обоснование интервьюера |
| `skills` | `{skill: [score]}` | запасной источник оценок, если `evaluation_log` не передан |
| `weaknesses` | `[str]` | слабые места, найденные интервьюерами |
| `target_position` | `str` | позиция, на которую проходило интервью |
| `experience_level` | `intern` / `junior` / `middle` / `senior` | заявленный уровень |
| `resume_topics` | `[str]` | темы из резюме |
| `resume_experience` | `{тема: лет}` | опыт по темам |
| `session_id` | `str` | необязательно, в анализе не участвует |

Обязательных полей нет, но в запросе должен быть хотя бы один ответ кандидата в `messages` либо
оценки в `evaluation_log` / `skills`. Иначе вернётся `422`.

**Выход:**

```json
{
  "stats": {
    "answered_questions": 6,
    "overall_score": 5.8,
    "overall_band": "basic",
    "overall_band_label": "базовый",
    "is_preliminary": false,
    "by_agent": {"hr": 5.0, "tech": 7.3, "manager": 3.0},
    "skills": [
      {"skill": "tech.async", "agent": "tech", "topic": "async", "average": 8.0, "count": 1, "scores": [8]}
    ],
    "strongest": ["tech.decorators", "tech.async"],
    "weakest": ["manager.planning", "hr.conflict"]
  },
  "feedback": {
    "summary": "Результат базовый, ниже заявленного уровня middle. Технические навыки сильнее (7.3), HR и менеджерские блоки слабее среднего.",
    "strengths": ["Уверенно объясняет asyncio и разницу с threading."],
    "weaknesses": ["Не привёл примера по теме конфликтов.", "Поверхностно знает оптимизацию SQL."],
    "recommendations": ["Разобрать типы индексов в PostgreSQL и чтение плана EXPLAIN ANALYZE."]
  }
}
```

(Пример сокращён; в `skills` показана одна запись.)

**Блок `stats`**:

| Поле | Значение |
|---|---|
| `answered_questions` | сколько ответов дал кандидат |
| `overall_score` | среднее по всем оценкам, 0–10 (`null`, если оценок нет) |
| `overall_band` / `overall_band_label` | уровень по шкале интервьюеров: `weak` / слабый (<4), `basic` / базовый (4–6.9), `good` / хороший (7–8.9), `excellent` / отличный (≥9) |
| `is_preliminary` | `true`, если оценок меньше трёх: выводы предварительные |
| `by_agent` | средняя оценка по этапам |
| `skills` | оценки по каждой теме |
| `strongest` / `weakest` | до двух лучших и худших тем; пустые, если оценки по темам одинаковы |

**Блок `feedback`** пишет модель. Все четыре поля всегда присутствуют; `strengths` может быть
пустым списком: сильные стороны не выдумываются.

### `POST /v1/chat`: вопросы по результатам

```json
{
  "interview": { "...": "тот же объект, что во входе /v1/feedback" },
  "feedback": {"summary": "...", "strengths": [], "weaknesses": ["..."], "recommendations": ["..."]},
  "history": [
    {"role": "user", "content": "Привет"},
    {"role": "assistant", "content": "Здравствуйте! Спрашивайте."}
  ],
  "question": "Почему за SQL только 5 и как это исправить?"
}
```

`feedback` и `history` можно не передавать. `question` обязателен, от 1 до 2000 символов.
Ответ: `{"answer": "..."}`.

Аналитик отвечает только по данным интервью, не придумывает слова интервьюера и **не меняет
оценки**: если просят пересмотреть, объясняет, на чём они держатся.

### Ошибки

Все ошибки приходят в JSON с полем `detail`.

| Код | Когда |
|---|---|
| `422` | нет данных для анализа; оценка вне диапазона 0–10; пустой `question`; неверные типы полей |
| `502` | GigaChat недоступен, ключ не принят или модель не вернула валидный ответ после повторов |

`422` значит «проблема во входных данных», `502` — «сбой зависимости»: запрос можно повторить позже.

## Настройки

Читаются из `.env` или переменных окружения (шаблон: `.env.example`).

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `GIGACHAT_CREDENTIALS` | | ключ авторизации GigaChat |
| `GIGACHAT_SCOPE` | `GIGACHAT_API_PERS` | scope |
| `GIGACHAT_MODEL` | `GigaChat-2-Pro` | модель |
| `GIGACHAT_VERIFY_SSL` | `false` | проверка SSL (как у остальных агентов) |
| `MAX_TOKENS` | `2048` | лимит длины ответа модели |
| `MAX_DIALOG_CHARS` | `12000` | сколько символов диалога передавать в промпт |
| `MAX_MESSAGE_CHARS` | `1500` | предел длины одной реплики |
| `MAX_CHAT_HISTORY` | `20` | сколько последних сообщений чата учитывать |

После изменения `.env` сервис нужно перезапустить.

## Структура проекта

```
analyst_agent/
├── app/
│   ├── main.py       # HTTP: эндпоинты и обработка ошибок (FastAPI)
│   ├── graph.py      # граф LangGraph: порядок шагов и сборка промптов
│   ├── stats.py      # подсчёт статистики и подготовка диалога, без LLM
│   ├── llm.py        # вызов GigaChat; повторы при сбоях
│   ├── prompts.py    # тексты промптов (шкала, правила, формат)
│   ├── schemas.py    # контракт: входные и выходные модели (pydantic)
│   └── config.py     # настройки из .env
├── samples/          # примеры входных данных (вымышленные)
├── tests/            # автотесты
├── requirements.txt  # зависимости сервиса
├── Dockerfile
└── .env.example
```

## Тесты

```bash
pip install -r requirements-dev.txt
pytest -q # 28 тестов
```

Обращения к модели в тестах подменены заглушкой: тесты проверяют логику (подсчёты,
валидацию, коды ошибок, содержимое промпта), а не качество ответов модели. Качество текста
проверяется вручную на примерах из `samples/`:

- `sample_state.json`: кандидат среднего уровня с неровными оценками;
- `sample_state_weak.json`: слабый кандидат, в ответе есть попытка prompt injection.
  Оценки и фидбек не должны ей поддаться.

## Docker

```bash
docker build -t analyst_agent .
docker run --env-file .env -p 8002:8000 analyst_agent
```

