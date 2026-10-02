import type {
  AuthResponse,
  ExperienceLevel,
  InterviewResponse,
  InterviewSession,
  ResumeResult,
} from "./types";

const API_ROOT = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(`${API_ROOT}${path}`, { ...options, headers });
  } catch {
    throw new ApiError("Не удалось связаться с сервером. Проверьте, что backend запущен.", 0);
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail;
    const message = typeof detail === "string" ? detail : "Сервер не смог выполнить запрос";
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}

export const api = {
  signIn: (email: string, password: string) =>
    request<AuthResponse>("/auth/sign-in", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  signUp: (email: string, password: string) =>
    request<AuthResponse>("/auth/sign-up", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  listSessions: (token: string) => request<InterviewSession[]>("/sessions", {}, token),

  createSession: (
    token: string,
    payload: { title: string; target_position: string; experience_level: ExperienceLevel },
  ) =>
    request<InterviewSession>(
      "/sessions",
      { method: "POST", body: JSON.stringify(payload) },
      token,
    ),

  uploadResume: (token: string, sessionId: string, file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<ResumeResult>(
      `/sessions/${sessionId}/resume`,
      { method: "POST", body },
      token,
    );
  },

  getInterview: (token: string, sessionId: string) =>
    request<InterviewResponse>(`/sessions/${sessionId}/interview`, {}, token),

  startInterview: (token: string, sessionId: string) =>
    request<InterviewResponse>(
      `/sessions/${sessionId}/interview/start`,
      { method: "POST" },
      token,
    ),

  answerInterview: (token: string, sessionId: string, answer: string) =>
    request<InterviewResponse>(
      `/sessions/${sessionId}/interview/answer`,
      { method: "POST", body: JSON.stringify({ answer }) },
      token,
    ),
};
