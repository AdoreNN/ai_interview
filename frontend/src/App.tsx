import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import { api, ApiError } from "./api";
import { Icon } from "./Icons";
import type {
  ChatMessage,
  ExperienceLevel,
  InterviewResponse,
  InterviewSession,
} from "./types";

const demoSessions: InterviewSession[] = [
  {
    id: "demo-product",
    title: "Product designer · Яндекс",
    target_position: "Senior Product Designer",
    experience_level: "senior",
    status: "in_progress",
    has_resume: true,
    interview_started: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "demo-python",
    title: "Python developer",
    target_position: "Middle Python Developer",
    experience_level: "middle",
    status: "completed",
    has_resume: true,
    interview_started: true,
    created_at: new Date(Date.now() - 86_400_000).toISOString(),
    updated_at: new Date(Date.now() - 86_400_000).toISOString(),
  },
  {
    id: "demo-analyst",
    title: "Системный аналитик",
    target_position: "Junior System Analyst",
    experience_level: "junior",
    status: "created",
    has_resume: false,
    interview_started: false,
    created_at: new Date(Date.now() - 172_800_000).toISOString(),
    updated_at: new Date(Date.now() - 172_800_000).toISOString(),
  },
];

const initialDemoInterview: InterviewResponse = {
  status: "in_progress",
  current_question:
    "Представьте, что после запуска нового онбординга конверсия выросла, но количество обращений в поддержку увеличилось на 35%. Как вы будете разбираться в ситуации?",
  messages: [
    {
      role: "assistant",
      content:
        "Привет! Я изучил ваше резюме и подготовил вопросы под позицию Senior Product Designer. Начнём с небольшого знакомства, затем перейдём к кейсам и продуктовым решениям.",
    },
    {
      role: "assistant",
      content: "Расскажите о проекте, в котором ваше дизайнерское решение заметно повлияло на продуктовую метрику.",
    },
    {
      role: "user",
      content:
        "В финтех-приложении я переработал первый сценарий перевода. Мы начали с анализа воронки и интервью с пользователями, после чего сократили путь с пяти шагов до трёх. Конверсия в завершённый перевод выросла на 18%.",
    },
    {
      role: "assistant",
      content:
        "Представьте, что после запуска нового онбординга конверсия выросла, но количество обращений в поддержку увеличилось на 35%. Как вы будете разбираться в ситуации?",
    },
  ],
  evaluation_log: [
    {
      skill: "hr.impact",
      score: 8,
      reason: "Ответ содержит контекст, действие и измеримый результат.",
    },
  ],
  final_feedback: null,
};

const demoFollowups = [
  "Какие качественные и количественные данные вы соберёте в первую очередь и почему?",
  "Команда не согласна с вашим решением, а сроки не позволяют провести полноценное исследование. Как будете действовать?",
];

const experienceLabels: Record<ExperienceLevel, string> = {
  intern: "Intern",
  junior: "Junior",
  middle: "Middle",
  senior: "Senior",
};

function messageFor(error: unknown) {
  if (error instanceof ApiError) return error.message;
  return "Что-то пошло не так. Попробуйте ещё раз.";
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("grillo_token") ?? "");
  const [email, setEmail] = useState(() => localStorage.getItem("grillo_email") ?? "");
  const [demoMode, setDemoMode] = useState(false);
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [interview, setInterview] = useState<InterviewResponse | null>(null);
  const [showAuth, setShowAuth] = useState(!token);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token || demoMode) return;
    void refreshSessions(token);
  }, [token, demoMode]);

  async function refreshSessions(activeToken: string) {
    setLoading(true);
    setError("");
    try {
      const items = await api.listSessions(activeToken);
      setSessions(items);
      if (!selectedId && items[0]) await chooseSession(items[0], activeToken);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) logout();
      else setError(messageFor(err));
    } finally {
      setLoading(false);
    }
  }

  async function chooseSession(session: InterviewSession, activeToken = token) {
    setSelectedId(session.id);
    setSidebarOpen(false);
    setError("");
    if (!session.interview_started) {
      setInterview(null);
      return;
    }
    if (demoMode || session.id.startsWith("demo-")) {
      setInterview(initialDemoInterview);
      return;
    }
    setLoading(true);
    try {
      setInterview(await api.getInterview(activeToken, session.id));
    } catch (err) {
      setError(messageFor(err));
      setInterview(null);
    } finally {
      setLoading(false);
    }
  }

  function enterDemo() {
    setDemoMode(true);
    setSessions(demoSessions);
    setSelectedId(demoSessions[0].id);
    setInterview(initialDemoInterview);
    setEmail("demo@grillo.ai");
    setShowAuth(false);
  }

  function logout() {
    localStorage.removeItem("grillo_token");
    localStorage.removeItem("grillo_email");
    setToken("");
    setEmail("");
    setDemoMode(false);
    setSessions([]);
    setSelectedId(null);
    setInterview(null);
    setShowAuth(true);
  }

  const selectedSession = sessions.find((item) => item.id === selectedId) ?? null;

  if (showAuth) {
    return (
      <AuthScreen
        onAuthenticated={(auth) => {
          localStorage.setItem("grillo_token", auth.access_token);
          localStorage.setItem("grillo_email", auth.email);
          setToken(auth.access_token);
          setEmail(auth.email);
          setShowAuth(false);
        }}
        onDemo={enterDemo}
      />
    );
  }

  return (
    <div className="app-shell">
      <Sidebar
        open={sidebarOpen}
        sessions={sessions}
        selectedId={selectedId}
        email={email}
        demoMode={demoMode}
        onClose={() => setSidebarOpen(false)}
        onNew={() => {
          setSelectedId(null);
          setInterview(null);
          setSidebarOpen(false);
        }}
        onSelect={(item) => void chooseSession(item)}
        onLogout={logout}
      />

      <main className="main-panel">
        {error && (
          <div className="toast" role="alert">
            <span>{error}</span>
            <button aria-label="Закрыть сообщение" onClick={() => setError("")}>
              <Icon name="close" />
            </button>
          </div>
        )}

        <Topbar
          session={selectedSession}
          interview={interview}
          loading={loading}
          onMenu={() => setSidebarOpen(true)}
        />

        {selectedSession?.interview_started && interview ? (
          <InterviewView
            session={selectedSession}
            interview={interview}
            loading={loading}
            demoMode={demoMode}
            onInterviewChange={setInterview}
            onError={(value) => setError(value)}
            token={token}
          />
        ) : (
          <SetupView
            existingSession={selectedSession}
            loading={loading}
            demoMode={demoMode}
            token={token}
            onLoading={setLoading}
            onError={setError}
            onReady={(session, nextInterview) => {
              setSessions((items) => [session, ...items.filter((item) => item.id !== session.id)]);
              setSelectedId(session.id);
              setInterview(nextInterview);
            }}
          />
        )}
      </main>
    </div>
  );
}

function AuthScreen({
  onAuthenticated,
  onDemo,
}: {
  onAuthenticated: (auth: { access_token: string; email: string }) => void;
  onDemo: () => void;
}) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const auth = isSignUp ? await api.signUp(email, password) : await api.signIn(email, password);
      onAuthenticated(auth);
    } catch (err) {
      setError(messageFor(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-layout">
      <section className="auth-story">
        <div className="brand brand--large">
          <span className="brand-mark">g</span>
          <span>grillo</span>
        </div>
        <div className="auth-copy">
          <p className="eyebrow">AI INTERVIEW PRACTICE</p>
          <h1>Собеседование, после которого становишься сильнее.</h1>
          <p>
            Персональные вопросы по вашему резюме, честная оценка ответов и понятный план роста.
          </p>
        </div>
        <div className="auth-preview" aria-hidden="true">
          <span className="preview-dot" />
          <div>
            <small>GRILLO · TECH</small>
            <p>Как бы вы объяснили это решение команде?</p>
          </div>
          <span className="preview-score">8.4</span>
        </div>
      </section>

      <section className="auth-form-wrap">
        <form className="auth-form" onSubmit={submit}>
          <div>
            <p className="eyebrow">{isSignUp ? "НОВЫЙ АККАУНТ" : "С ВОЗВРАЩЕНИЕМ"}</p>
            <h2>{isSignUp ? "Начать подготовку" : "Войти в Grillo"}</h2>
            <p className="muted">
              {isSignUp ? "Создайте аккаунт за минуту." : "Продолжите с того места, где остановились."}
            </p>
          </div>

          <label>
            <span>Электронная почта</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </label>
          <label>
            <span>Пароль</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Минимум 8 символов"
              autoComplete={isSignUp ? "new-password" : "current-password"}
              minLength={isSignUp ? 8 : 1}
              required
            />
          </label>

          {error && <p className="form-error">{error}</p>}

          <button className="button button--primary button--wide" disabled={loading} type="submit">
            {loading ? <span className="spinner" /> : isSignUp ? "Создать аккаунт" : "Войти"}
            {!loading && <Icon name="arrow" />}
          </button>

          <button className="button button--ghost button--wide" type="button" onClick={onDemo}>
            Посмотреть демо
          </button>

          <p className="auth-switch">
            {isSignUp ? "Уже есть аккаунт?" : "Впервые здесь?"}{" "}
            <button type="button" onClick={() => setIsSignUp((value) => !value)}>
              {isSignUp ? "Войти" : "Зарегистрироваться"}
            </button>
          </p>
        </form>
      </section>
    </div>
  );
}

function Sidebar({
  open,
  sessions,
  selectedId,
  email,
  demoMode,
  onClose,
  onNew,
  onSelect,
  onLogout,
}: {
  open: boolean;
  sessions: InterviewSession[];
  selectedId: string | null;
  email: string;
  demoMode: boolean;
  onClose: () => void;
  onNew: () => void;
  onSelect: (session: InterviewSession) => void;
  onLogout: () => void;
}) {
  return (
    <>
      <button
        className={`sidebar-backdrop ${open ? "is-visible" : ""}`}
        aria-label="Закрыть меню"
        onClick={onClose}
      />
      <aside className={`sidebar ${open ? "is-open" : ""}`}>
        <div className="sidebar-head">
          <div className="brand">
            <span className="brand-mark">g</span>
            <span>grillo</span>
            {demoMode && <span className="demo-badge">demo</span>}
          </div>
          <button className="icon-button mobile-only" aria-label="Закрыть меню" onClick={onClose}>
            <Icon name="close" />
          </button>
        </div>

        <button className="new-chat" onClick={onNew}>
          <Icon name="plus" />
          <span>Новое интервью</span>
          <kbd>⌘ N</kbd>
        </button>

        <nav className="sidebar-nav" aria-label="Основная навигация">
          <button className="nav-row is-active">
            <Icon name="chat" />
            <span>Интервью</span>
          </button>
          <button className="nav-row">
            <Icon name="file" />
            <span>Мои резюме</span>
            <span className="soon">скоро</span>
          </button>
        </nav>

        <div className="history">
          <p className="section-label">НЕДАВНИЕ</p>
          <div className="history-list">
            {sessions.map((session) => (
              <button
                key={session.id}
                className={`history-item ${selectedId === session.id ? "is-active" : ""}`}
                onClick={() => onSelect(session)}
              >
                <span className={`status-dot status-dot--${session.status}`} />
                <span className="history-copy">
                  <strong>{session.title}</strong>
                  <small>{experienceLabels[session.experience_level]}</small>
                </span>
                <Icon name="more" />
              </button>
            ))}
            {sessions.length === 0 && <p className="history-empty">Здесь появятся ваши интервью.</p>}
          </div>
        </div>

        <div className="sidebar-foot">
          <button className="nav-row">
            <Icon name="settings" />
            <span>Настройки</span>
          </button>
          <div className="profile-row">
            <span className="avatar">{email.slice(0, 1).toUpperCase() || "G"}</span>
            <span className="profile-copy">
              <strong>{demoMode ? "Демо-профиль" : email.split("@")[0]}</strong>
              <small>{demoMode ? "Локальный режим" : email}</small>
            </span>
            <button className="icon-button" aria-label="Выйти" onClick={onLogout}>
              <Icon name="logout" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

function Topbar({
  session,
  interview,
  loading,
  onMenu,
}: {
  session: InterviewSession | null;
  interview: InterviewResponse | null;
  loading: boolean;
  onMenu: () => void;
}) {
  const stage = interview?.status === "completed" ? "Завершено" : interview ? "Интервью идёт" : "Подготовка";
  return (
    <header className="topbar">
      <button className="icon-button mobile-only" aria-label="Открыть меню" onClick={onMenu}>
        <Icon name="menu" />
      </button>
      <div className="topbar-title">
        <strong>{session?.title ?? "Новое интервью"}</strong>
        <span>{loading ? "Обновляем…" : stage}</span>
      </div>
      {interview && (
        <div className="stage-pill">
          <span className={interview.status === "completed" ? "pulse pulse--done" : "pulse"} />
          {interview.status === "completed" ? "Итоги готовы" : "Сессия активна"}
        </div>
      )}
    </header>
  );
}

function SetupView({
  existingSession,
  loading,
  demoMode,
  token,
  onLoading,
  onError,
  onReady,
}: {
  existingSession: InterviewSession | null;
  loading: boolean;
  demoMode: boolean;
  token: string;
  onLoading: (value: boolean) => void;
  onError: (value: string) => void;
  onReady: (session: InterviewSession, interview: InterviewResponse) => void;
}) {
  const [position, setPosition] = useState(existingSession?.target_position ?? "");
  const [title, setTitle] = useState(existingSession?.title ?? "");
  const [level, setLevel] = useState<ExperienceLevel>(existingSession?.experience_level ?? "middle");
  const [file, setFile] = useState<File | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setPosition(existingSession?.target_position ?? "");
    setTitle(existingSession?.title ?? "");
    setLevel(existingSession?.experience_level ?? "middle");
    setFile(null);
  }, [existingSession?.id]);

  async function begin(event: FormEvent) {
    event.preventDefault();
    if (!position.trim()) return;
    onLoading(true);
    onError("");
    try {
      if (demoMode) {
        await new Promise((resolve) => window.setTimeout(resolve, 550));
        const session: InterviewSession = {
          id: `demo-${Date.now()}`,
          title: title.trim() || position.trim(),
          target_position: position.trim(),
          experience_level: level,
          status: "in_progress",
          has_resume: Boolean(file),
          interview_started: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        onReady(session, {
          ...initialDemoInterview,
          messages: [
            {
              role: "assistant",
              content: `Привет! Начинаем тренировку на позицию «${position.trim()}». Я буду задавать вопросы по одному и в конце соберу обратную связь.`,
            },
            { role: "assistant", content: "Расскажите коротко о себе и опыте, который лучше всего подходит этой роли." },
          ],
          current_question: "Расскажите коротко о себе и опыте, который лучше всего подходит этой роли.",
          evaluation_log: [],
        });
        return;
      }

      let session = existingSession;
      if (!session) {
        session = await api.createSession(token, {
          title: title.trim() || position.trim(),
          target_position: position.trim(),
          experience_level: level,
        });
      }
      if (file) await api.uploadResume(token, session.id, file);
      const nextInterview = await api.startInterview(token, session.id);
      onReady({ ...session, has_resume: Boolean(file) || session.has_resume, interview_started: true, status: "in_progress" }, nextInterview);
    } catch (err) {
      onError(messageFor(err));
    } finally {
      onLoading(false);
    }
  }

  return (
    <div className="setup-scroll">
      <div className="setup-container">
        <div className="setup-intro">
          <span className="setup-icon"><Icon name="spark" /></span>
          <p className="eyebrow">НОВАЯ ТРЕНИРОВКА</p>
          <h1>К какой роли готовимся?</h1>
          <p>Настройте контекст — Grillo соберёт интервью под нужный уровень и ваш опыт.</p>
        </div>

        <form className="setup-form" onSubmit={begin}>
          <section className="setup-section">
            <div className="setup-section-head">
              <span>01</span>
              <div>
                <h2>Целевая позиция</h2>
                <p>Используем её для сложности и тем вопросов.</p>
              </div>
            </div>
            <div className="field-grid">
              <label className="field field--wide">
                <span>Позиция</span>
                <input
                  value={position}
                  onChange={(event) => setPosition(event.target.value)}
                  placeholder="Например, Product Designer"
                  required
                  disabled={Boolean(existingSession)}
                />
              </label>
              <label className="field field--wide">
                <span>Название сессии <em>необязательно</em></span>
                <input
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="Собеседование в компанию"
                  disabled={Boolean(existingSession)}
                />
              </label>
            </div>
          </section>

          <section className="setup-section">
            <div className="setup-section-head">
              <span>02</span>
              <div>
                <h2>Уровень опыта</h2>
                <p>Влияет на глубину и ожидаемую самостоятельность.</p>
              </div>
            </div>
            <div className="segmented" role="radiogroup" aria-label="Уровень опыта">
              {(Object.keys(experienceLabels) as ExperienceLevel[]).map((value) => (
                <button
                  className={level === value ? "is-selected" : ""}
                  type="button"
                  role="radio"
                  aria-checked={level === value}
                  onClick={() => setLevel(value)}
                  disabled={Boolean(existingSession)}
                  key={value}
                >
                  {experienceLabels[value]}
                </button>
              ))}
            </div>
          </section>

          <section className="setup-section">
            <div className="setup-section-head">
              <span>03</span>
              <div>
                <h2>Резюме</h2>
                <p>Необязательно, но с ним вопросы будут персональнее.</p>
              </div>
            </div>
            <input
              ref={fileInput}
              className="visually-hidden"
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
            <button className={`dropzone ${file ? "has-file" : ""}`} type="button" onClick={() => fileInput.current?.click()}>
              <span className="dropzone-icon"><Icon name={file ? "check" : "upload"} /></span>
              <span>
                <strong>{file ? file.name : "Добавить PDF-резюме"}</strong>
                <small>{file ? `${(file.size / 1024 / 1024).toFixed(1)} МБ · готово к анализу` : "до 5 МБ · данные останутся внутри сессии"}</small>
              </span>
              <span className="dropzone-action">{file ? "Заменить" : "Выбрать файл"}</span>
            </button>
          </section>

          <div className="setup-actions">
            <p><Icon name="brain" /> Обычно интервью занимает 20–30 минут</p>
            <button className="button button--primary" type="submit" disabled={loading || !position.trim()}>
              {loading ? <><span className="spinner" /> Готовим вопросы</> : <>Начать интервью <Icon name="arrow" /></>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function InterviewView({
  session,
  interview,
  loading,
  demoMode,
  token,
  onInterviewChange,
  onError,
}: {
  session: InterviewSession;
  interview: InterviewResponse;
  loading: boolean;
  demoMode: boolean;
  token: string;
  onInterviewChange: (value: InterviewResponse) => void;
  onError: (value: string) => void;
}) {
  const [answer, setAnswer] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  const scoreCount = interview.evaluation_log.length;
  const progress = interview.status === "completed" ? 100 : Math.min(92, 12 + scoreCount * 13);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [interview.messages.length, sending]);

  async function submitAnswer() {
    const value = answer.trim();
    if (!value || sending || interview.status === "completed") return;
    setAnswer("");
    if (textarea.current) textarea.current.style.height = "auto";
    setSending(true);
    onError("");
    const optimistic: ChatMessage[] = [...interview.messages, { role: "user", content: value }];
    onInterviewChange({ ...interview, messages: optimistic });
    try {
      if (demoMode) {
        await new Promise((resolve) => window.setTimeout(resolve, 850));
        const nextIndex = scoreCount;
        const nextQuestion = demoFollowups[nextIndex] ?? null;
        if (nextQuestion) {
          onInterviewChange({
            ...interview,
            messages: [...optimistic, { role: "assistant", content: nextQuestion }],
            current_question: nextQuestion,
            evaluation_log: [
              ...interview.evaluation_log,
              { skill: `tech.case_${nextIndex + 1}`, score: 7 + (nextIndex % 2), reason: "Ответ структурирован и опирается на данные." },
            ],
          });
        } else {
          onInterviewChange({
            ...interview,
            messages: optimistic,
            current_question: null,
            status: "completed",
            evaluation_log: [...interview.evaluation_log, { skill: "manager.collaboration", score: 8, reason: "Зрелый подход к коммуникации." }],
            final_feedback: {
              skill_averages: { "product thinking": 8.2, communication: 8, analytics: 7.4 },
              weaknesses: ["Чётче формулировать критерии принятия решения", "Раньше обозначать риски эксперимента"],
            },
          });
        }
      } else {
        onInterviewChange(await api.answerInterview(token, session.id, value));
      }
    } catch (err) {
      onInterviewChange(interview);
      setAnswer(value);
      onError(messageFor(err));
    } finally {
      setSending(false);
    }
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submitAnswer();
    }
  }

  return (
    <div className="interview-layout">
      <div className="progress-strip">
        <div className="progress-meta">
          <span>ПРОГРЕСС</span>
          <strong>{interview.status === "completed" ? "100%" : `${progress}%`}</strong>
        </div>
        <div className="progress-track"><span style={{ width: `${progress}%` }} /></div>
        <div className="stage-list">
          <span className="is-done"><Icon name="check" /> Знакомство</span>
          <span className={scoreCount > 0 ? "is-current" : ""}>Кейсы</span>
          <span className={scoreCount > 2 ? "is-current" : ""}>Команда</span>
          <span className={interview.status === "completed" ? "is-done" : ""}>Итоги</span>
        </div>
      </div>

      <div className="conversation" aria-live="polite">
        <div className="conversation-inner">
          <div className="session-kicker">
            <span>{experienceLabels[session.experience_level]}</span>
            <span>{session.target_position}</span>
            {session.has_resume && <span><Icon name="file" /> резюме учтено</span>}
          </div>

          {interview.messages.map((message, index) => (
            <Message key={`${index}-${message.content.slice(0, 12)}`} message={message} isLatest={index === interview.messages.length - 1} />
          ))}

          {sending && (
            <div className="message message--assistant">
              <div className="assistant-mark">g</div>
              <div className="thinking"><i /><i /><i /><span>анализирую ответ</span></div>
            </div>
          )}

          {interview.status === "completed" && interview.final_feedback && (
            <FeedbackCard interview={interview} />
          )}
          <div ref={endRef} />
        </div>
      </div>

      {interview.status !== "completed" ? (
        <div className="composer-wrap">
          <div className="composer">
            <textarea
              ref={textarea}
              value={answer}
              onChange={(event) => {
                setAnswer(event.target.value);
                event.target.style.height = "auto";
                event.target.style.height = `${Math.min(event.target.scrollHeight, 180)}px`;
              }}
              onKeyDown={onKeyDown}
              placeholder="Ответьте своими словами…"
              rows={1}
              disabled={sending || loading}
              aria-label="Ответ на вопрос"
            />
            <div className="composer-foot">
              <span><kbd>Enter</kbd> отправить · <kbd>Shift ↵</kbd> новая строка</span>
              <span className="char-count">{answer.length > 0 ? answer.length : ""}</span>
              <button
                className="send-button"
                aria-label="Отправить ответ"
                disabled={!answer.trim() || sending}
                onClick={() => void submitAnswer()}
              >
                <Icon name="arrow" />
              </button>
            </div>
          </div>
          <p className="composer-note">Grillo может ошибаться. Отвечайте так, как говорили бы живому интервьюеру.</p>
        </div>
      ) : (
        <div className="completion-bar">
          <span><Icon name="check" /> Интервью завершено</span>
          <button className="button button--secondary" onClick={() => window.print()}>Сохранить результат</button>
        </div>
      )}
    </div>
  );
}

function Message({ message, isLatest }: { message: ChatMessage; isLatest: boolean }) {
  if (message.role === "user") {
    return (
      <article className="message message--user">
        <div className="user-bubble">{message.content}</div>
      </article>
    );
  }
  return (
    <article className="message message--assistant">
      <div className="assistant-mark">g</div>
      <div className="assistant-content">
        {isLatest && <p className="message-label">СЛЕДУЮЩИЙ ВОПРОС</p>}
        <p>{message.content}</p>
      </div>
    </article>
  );
}

function FeedbackCard({ interview }: { interview: InterviewResponse }) {
  const scores = Object.entries(interview.final_feedback?.skill_averages ?? {});
  const average = scores.length ? scores.reduce((sum, [, value]) => sum + value, 0) / scores.length : 0;
  return (
    <section className="feedback-card">
      <div className="feedback-head">
        <div>
          <p className="eyebrow">ИТОГИ ИНТЕРВЬЮ</p>
          <h2>Хорошая работа.</h2>
          <p>Вы уверенно прошли основные блоки. Ниже — то, что уже получается, и точки роста.</p>
        </div>
        <div className="total-score"><strong>{average.toFixed(1)}</strong><span>/ 10</span></div>
      </div>
      <div className="score-grid">
        {scores.map(([skill, score]) => (
          <div className="score-row" key={skill}>
            <div><span>{skill.replaceAll("_", " ")}</span><strong>{score.toFixed(1)}</strong></div>
            <div className="score-track"><span style={{ width: `${score * 10}%` }} /></div>
          </div>
        ))}
      </div>
      {(interview.final_feedback?.weaknesses?.length ?? 0) > 0 && (
        <div className="growth-list">
          <p className="section-label">ТОЧКИ РОСТА</p>
          {interview.final_feedback?.weaknesses?.map((item, index) => (
            <div key={item}><span>0{index + 1}</span><p>{item}</p></div>
          ))}
        </div>
      )}
    </section>
  );
}

export default App;
