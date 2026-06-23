export type User = {
  id: string;
  phone_masked: string;
  full_name: string;
  region: string;
  language: "ru" | "uz";
  role: "citizen" | "moderator" | "admin";
  points: number;
  is_verified: boolean;
  date_joined: string;
};

export type QuizChoice = {
  id: string;
  text: string;
  order: number;
};

export type QuizQuestion = {
  id: string;
  text: string;
  category: string;
  difficulty: string;
  choices: QuizChoice[];
};

export type QuizSession = {
  session_id: string;
  question_count: number;
  expires_in: number;
  questions: QuizQuestion[];
};

export type QuizResult = {
  session_id: string;
  score: number;
  level: "none" | "basic" | "advanced" | "expert";
  passed: boolean;
  certificate_id: string | null;
  answers: {
    question_id: string;
    selected_choice_id: string;
    correct_choice_id: string;
    is_correct: boolean;
    explanation: string;
  }[];
};

export type Certificate = {
  id: string;
  owner_name: string;
  level: string;
  score: number;
  issued_at: string;
  is_valid: boolean;
  verification_url: string;
  pdf_url: string;
};

export type NumberCheck = {
  found: boolean;
  status: string;
  message?: string;
  phone_masked?: string;
  approved_reports_count?: number;
  scam_types?: string[];
  first_reported_at?: string;
  last_reported_at?: string;
  reports?: {
    scam_type: string;
    incident_date: string;
    story: string;
    region: string;
  }[];
};

export type AnalysisResult = {
  analysis_id: string;
  verdict: "safe" | "suspicious" | "dangerous";
  risk_score: number;
  reasons: string[];
  signals: string[];
  privacy: string;
};

export type Course = {
  id: string;
  slug: string;
  title: string;
  description: string;
  level: "basic" | "advanced" | "expert";
  duration_minutes: number;
  lessons_count: number;
  completed_lessons: number;
  progress_percent: number;
};

export type CourseLesson = {
  id: string;
  title: string;
  summary: string;
  duration_minutes: number;
  order: number;
  completed: boolean;
};

export type CourseDetail = Course & {
  lessons: CourseLesson[];
};

export type LessonDetail = {
  id: string;
  course_id: string;
  title: string;
  summary: string;
  content: string;
  video_url: string;
  duration_minutes: number;
  order: number;
  completed: boolean;
  question: null | {
    text: string;
    choices: {
      id: string;
      text: string;
      order: number;
    }[];
  };
};

export type GameScenario = {
  id: string;
  slug: string;
  title: string;
  description: string;
  scam_type: string;
  difficulty: "easy" | "medium" | "hard";
  steps_count: number;
};

export type GameState = {
  id: string;
  status: "active" | "completed";
  scenario_title: string;
  step_number: number | null;
  total_steps: number;
  message: string | null;
  choices: {
    id: string;
    text: string;
    order: number;
  }[];
  score_percent: number | null;
  points_awarded: number;
};

export type GameResult = {
  session_id: string;
  scenario_title: string;
  score_percent: number;
  points_awarded: number;
  level: "expert" | "resistant" | "vulnerable";
  ai_analysis: string;
  ai_used: boolean;
  ai_model: string;
  turns: {
    step: number;
    message: string;
    answer: string;
    feedback: string;
    tactic: string;
    points: number;
  }[];
};

export type ModerationReport = {
  id: string;
  phone_masked: string;
  scam_type: string;
  incident_date: string;
  story: string;
  region: string;
  damage_amount: string | null;
  status: "pending" | "approved" | "rejected";
  moderator_comment: string;
  created_at: string;
  reporter_id: string;
  reporter_name: string;
  number_id: string;
  number_status: "reported" | "suspicious" | "scammer" | "verified_scammer";
  approved_reports_count: number;
  number_verified: boolean;
  moderated_at: string | null;
};

export type ModerationSummary = {
  pending: number;
  approved: number;
  rejected: number;
  verified_numbers: number;
  reports_today: number;
};
