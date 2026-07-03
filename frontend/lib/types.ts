export type User = {
  id: string;
  phone_masked: string;
  full_name: string;
  region: string;
  language: "ru" | "uz";
  role: "citizen" | "moderator" | "admin";
  points: number;
  rank: number;
  is_verified: boolean;
  date_joined: string;
};

export type AdminUser = User & {
  is_active: boolean;
  is_staff: boolean;
  updated_at: string;
};

export type LeaderboardEntry = {
  rank: number;
  user_name: string;
  points: number;
  is_current_user: boolean;
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
  kind?: "standard" | "daily";
  question_count: number;
  expires_in: number;
  questions: QuizQuestion[];
};

export type DailyQuizStatus = {
  date: string;
  completed: boolean;
  started: boolean;
  session_id: string | null;
  score: number | null;
  streak: number;
  total_completed: number;
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
  module_title: string;
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
  course_title: string;
  course_lessons: CourseLesson[];
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
  questions?: {
    text: string;
    choices: {
      id: string;
      text: string;
      order: number;
    }[];
  }[];
  blocks?: {
    id: string;
    type:
      | "theory"
      | "definition"
      | "example"
      | "warning"
      | "note"
      | "code"
      | "checklist"
      | "task"
      | "quiz"
      | "materials";
    title: string;
    body: string;
    data: {
      items?: (string | { ru?: string; uz?: string; text?: string })[];
      links?: {
        title: string;
        url: string;
      }[];
      [key: string]: unknown;
    };
    order: number;
  }[];
  tasks?: {
    id: string;
    type: "text" | "checklist" | "sorting" | "scenario";
    title: string;
    instruction: string;
    data: {
      items?: {
        text: string | { ru?: string; uz?: string };
        text_ru?: string;
        text_uz?: string;
        risk?: string;
        category?: string;
      }[];
      options?: string[];
      [key: string]: unknown;
    };
    order: number;
  }[];
};

export type GameScenario = {
  id: string;
  slug: string;
  title: string;
  description: string;
  scam_type: string;
  interface_type: "chat" | "call" | "website";
  difficulty: "easy" | "medium" | "hard";
  steps_count: number;
};

export type GameState = {
  id: string;
  status: "active" | "completed";
  scenario_title: string;
  interface_type: "chat" | "call" | "website";
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
    selected_safe_intent: string;
    feedback: string;
    tactic: string;
    points: number;
  }[];
};

export type ModerationReport = {
  id: string;
  target_type: "phone" | "url" | "account" | "card" | "other";
  target_value: string;
  target_display: string;
  phone_masked: string;
  phone_full: string;
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
  number_id: string | null;
  number_status: "reported" | "suspicious" | "scammer" | "verified_scammer" | "";
  approved_reports_count: number;
  number_verified: boolean;
  moderated_at: string | null;
};

export type ModerationNumber = {
  number_id: string;
  phone_masked: string;
  phone_full: string;
  status: "reported" | "suspicious" | "scammer" | "verified_scammer";
  approved_reports_count: number;
  number_verified: boolean;
  scam_types: string[];
  first_reported_at: string | null;
  last_reported_at: string | null;
  verified_at: string | null;
  latest_reports: ModerationReport[];
};

export type ModerationSummary = {
  pending: number;
  approved: number;
  rejected: number;
  verified_numbers: number;
  reports_today: number;
};

export type AdminLesson = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  module_title: string;
  order: number;
  duration_minutes: number;
  is_published: boolean;
};

export type AdminCourseContent = {
  id: string;
  slug: string;
  title: string;
  level: "basic" | "advanced" | "expert";
  is_published: boolean;
  lessons_count: number;
  lessons: AdminLesson[];
};
