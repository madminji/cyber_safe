export type WebGameCharacter = {
  id: string;
  name: string;
  role: "analyst" | "defender" | "investigator" | "mentor";
  gender: "female" | "male";
  description: string;
  model_key: "amina" | "dilnoza" | "timur" | "jasur" | string;
  color_primary: string;
};

export type WebGameScenario = {
  id: string;
  slug: string;
  title: string;
  description: string;
  category: string;
  is_default: boolean;
  missions_count: number;
  locked: boolean;
};

export type WebGameStep = {
  id: string;
  order: number;
  task_type: "select_object" | "dialogue" | "secure_account";
  prompt: string;
  options: {
    value: string;
    label: string;
    kind: "safe" | "danger" | "warning" | "neutral" | string;
    color: string;
    position?: [number, number, number] | null;
  }[];
  points: number;
  penalty: number;
};

export type WebGameSession = {
  id: string;
  status: "active" | "completed";
  scenario_title: string;
  mission_title: string;
  scene_key: "cyber_office" | "inbox_room" | "account_lab" | "call_room" | string;
  character: WebGameCharacter;
  difficulty: "easy" | "medium" | "hard";
  score: number;
  max_score: number;
  points_awarded: number;
  steps: WebGameStep[];
};

export type WebGameActionResult = {
  correct: boolean;
  points_delta: number;
  score: number;
  feedback: string;
  completed: boolean;
};

export type WebGameCompleteResult = {
  session_id: string;
  scenario_title: string;
  mission_title: string;
  character_name: string;
  difficulty: "easy" | "medium" | "hard";
  score: number;
  max_score: number;
  score_percent: number;
  points_awarded: number;
  level: "expert" | "strong" | "practice";
  turns: {
    step: number;
    prompt: string;
    selected_value: string;
    selected_label: string;
    correct_value: string;
    correct_label: string;
    correct: boolean;
    points_delta: number;
    feedback: string;
  }[];
};

export type WebGameLeaderboardEntry = {
  rank: number;
  user_name: string;
  total_score: number;
  missions_completed: number;
};

export type WebGameProfile = {
  selected_character_id: string | null;
  total_score: number;
  missions_completed: number;
  last_played_at: string | null;
  recent_sessions: {
    id: string;
    scenario_title: string;
    difficulty: "easy" | "medium" | "hard";
    score: number;
    max_score: number;
    points_awarded: number;
    completed_at: string;
  }[];
};
