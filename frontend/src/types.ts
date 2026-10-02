export type ExperienceLevel = "intern" | "junior" | "middle" | "senior";
export type SessionStatus = "created" | "in_progress" | "completed";

export interface AuthResponse {
  id: string;
  email: string;
  access_token: string;
  token_type: string;
}

export interface InterviewSession {
  id: string;
  title: string;
  target_position: string;
  experience_level: ExperienceLevel;
  status: SessionStatus;
  has_resume: boolean;
  interview_started: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface Evaluation {
  skill: string;
  score: number;
  reason?: string | null;
}

export interface InterviewResponse {
  status: SessionStatus;
  current_question: string | null;
  final_feedback: {
    skill_averages?: Record<string, number>;
    weaknesses?: string[];
  } | null;
  evaluation_log: Evaluation[];
  messages: ChatMessage[];
}

export interface ResumeResult {
  parsed_resume: {
    resume_topics: string[];
    resume_experience: Record<string, number>;
    target_position: string | null;
    experience_level: ExperienceLevel | null;
  };
  questions: Array<{ topic: string; question: string; target_agent: string }>;
}
