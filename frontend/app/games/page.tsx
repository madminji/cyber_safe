"use client";

import {
  ArrowRight,
  Award,
  CheckCircle2,
  LockKeyhole,
  Play,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Trophy,
  UserRound,
  XCircle,
} from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import {
  WebGameActionResult,
  WebGameCharacter,
  WebGameCompleteResult,
  WebGameLeaderboardEntry,
  WebGameScenario,
  WebGameSession,
} from "@/lib/webgame-types";

const GameCanvas = dynamic(() => import("@/components/games/GameCanvas"), {
  ssr: false,
  loading: () => (
    <div className="game3d-canvas-fallback">
      <span className="loader" /> Loading 3D scene...
    </div>
  ),
});

const roleLabel = {
  ru: {
    analyst: "Аналитик",
    defender: "Защитник",
    investigator: "Расследователь",
    mentor: "Наставник",
  },
  uz: {
    analyst: "Tahlilchi",
    defender: "Himoyachi",
    investigator: "Tergovchi",
    mentor: "Mentor",
  },
} as const;

const difficultyLabel = {
  ru: {
    easy: "Лёгкий",
    medium: "Средний",
    hard: "Сложный",
  },
  uz: {
    easy: "Oson",
    medium: "O‘rta",
    hard: "Qiyin",
  },
} as const;

export default function GamesPage() {
  const { user, loading: authLoading, reloadUser } = useAuth();
  const { language } = useLanguage();
  const [characters, setCharacters] = useState<WebGameCharacter[]>([]);
  const [scenarios, setScenarios] = useState<WebGameScenario[]>([]);
  const [leaderboard, setLeaderboard] = useState<WebGameLeaderboardEntry[]>([]);
  const [selectedCharacter, setSelectedCharacter] =
    useState<WebGameCharacter | null>(null);
  const [selectedScenario, setSelectedScenario] =
    useState<WebGameScenario | null>(null);
  const [session, setSession] = useState<WebGameSession | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [feedback, setFeedback] = useState<WebGameActionResult | null>(null);
  const [result, setResult] = useState<WebGameCompleteResult | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  const copy = useMemo(
    () =>
      language === "uz"
        ? {
            eyebrow: "3D xavfsizlik o‘yini",
            title: "CyberSafe Missions",
            lead: "3D sahnada belgilarni tekshiring, xavfsiz qarorlar qabul qiling va kiberxavfsizlik ballarini to‘plang.",
            guest: "Mehmon rejimida faqat bitta mashq ochiq. Kirgandan keyin barcha missiyalar va reyting ochiladi.",
            chooseCharacter: "Personajni tanlang",
            chooseScenario: "Missiyani tanlang",
            start: "Boshlash",
            mission: "Missiya",
            score: "Ball",
            step: "Qadam",
            difficulty: "Qiyinlik",
            leaderboard: "Reyting",
            loginCta: "Natijani saqlash uchun kiring",
            completed: "Missiya yakunlandi",
            points: "platforma balli",
            again: "Yana o‘ynash",
            correct: "To‘g‘ri",
            wrong: "Xato",
            auto: "Qiyinlik avtomatik tanlanadi",
            currentTask: "Joriy vazifa",
            startHint: "Missiyani boshlang va obyektni tanlang.",
            review: "Missiya tahlili",
            selected: "Tanlangan:",
            expected: "To‘g‘ri javob:",
            noScores: "Hali natijalar yo‘q.",
          }
        : {
            eyebrow: "3D игра по безопасности",
            title: "CyberSafe Missions",
            lead: "Проверяйте признаки угроз в 3D-сцене, принимайте безопасные решения и зарабатывайте очки киберзащиты.",
            guest: "В гостевом режиме открыт только один сценарий. После входа откроются все миссии и рейтинг.",
            chooseCharacter: "Выберите персонажа",
            chooseScenario: "Выберите миссию",
            start: "Начать",
            mission: "Миссия",
            score: "Счёт",
            step: "Шаг",
            difficulty: "Сложность",
            leaderboard: "Рейтинг",
            loginCta: "Войдите, чтобы сохранить результат",
            completed: "Миссия завершена",
            points: "баллов платформы",
            again: "Играть снова",
            correct: "Верно",
            wrong: "Ошибка",
            auto: "Сложность выбирается автоматически",
            currentTask: "Текущее задание",
            startHint: "Начните миссию и выберите объект в 3D-сцене.",
            review: "Разбор миссии",
            selected: "Выбрано:",
            expected: "Правильный ответ:",
            noScores: "Пока нет результатов.",
          },
    [language],
  );

  useEffect(() => {
    setBusy(true);
    Promise.all([
      api<WebGameCharacter[]>(`/webgame/characters/?language=${language}`),
      api<WebGameScenario[]>(`/webgame/scenarios/?language=${language}`, {
        auth: Boolean(user),
      }),
      api<WebGameLeaderboardEntry[]>("/webgame/leaderboard/"),
    ])
      .then(([nextCharacters, nextScenarios, nextLeaderboard]) => {
        setCharacters(nextCharacters);
        setScenarios(nextScenarios);
        setLeaderboard(nextLeaderboard);
        setSelectedCharacter((current) => current || nextCharacters[0] || null);
        setSelectedScenario((current) => current || nextScenarios[0] || null);
      })
      .catch((requestError) => setError((requestError as Error).message))
      .finally(() => setBusy(false));
  }, [language, user]);

  const currentStep = session?.steps[stepIndex] || null;

  const startMission = async () => {
    if (!selectedCharacter || !selectedScenario) return;
    setBusy(true);
    setError("");
    setFeedback(null);
    setResult(null);
    setStepIndex(0);
    try {
      const nextSession = await api<WebGameSession>("/webgame/sessions/", {
        method: "POST",
        auth: Boolean(user),
        body: JSON.stringify({
          scenario_id: selectedScenario.id,
          character_id: selectedCharacter.id,
        }),
      });
      setSession(nextSession);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const selectObject = async (value: string) => {
    if (!session || !currentStep) return;
    setBusy(true);
    setError("");
    try {
      const action = await api<WebGameActionResult>(
        `/webgame/sessions/${session.id}/actions/?language=${language}`,
        {
          method: "POST",
          auth: Boolean(user),
          body: JSON.stringify({
            mission_step_id: currentStep.id,
            selected_value: value,
          }),
        },
      );
      setFeedback(action);
      setSession((current) =>
        current ? { ...current, score: action.score } : current,
      );
      if (action.completed) {
        const completed = await api<WebGameCompleteResult>(
          `/webgame/sessions/${session.id}/complete/?language=${language}`,
          {
            method: "POST",
            auth: Boolean(user),
          },
        );
        setResult(completed);
        if (user) await reloadUser();
        api<WebGameLeaderboardEntry[]>("/webgame/leaderboard/")
          .then(setLeaderboard)
          .catch(() => undefined);
      } else {
        setStepIndex((index) => index + 1);
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setSession(null);
    setFeedback(null);
    setResult(null);
    setStepIndex(0);
    setError("");
  };

  const changeCharacter = (character: WebGameCharacter) => {
    if (result) reset();
    setSelectedCharacter(character);
  };

  const changeScenario = (scenario: WebGameScenario) => {
    if (result) reset();
    setSelectedScenario(scenario);
  };

  return (
    <section className="page-section games-page">
      <div className="container games-container">
        <div className="games-hero">
          <div>
            <span className="eyebrow">
              <Sparkles size={16} /> {copy.eyebrow}
            </span>
            <h1>{copy.title}</h1>
            <p>{copy.lead}</p>
            {!authLoading && !user && (
              <div className="games-guest-note">
                <LockKeyhole size={17} /> {copy.guest}
              </div>
            )}
          </div>
          <Link href="/games/leaderboard" className="button button-ghost">
            <Trophy size={17} /> {copy.leaderboard}
          </Link>
        </div>

        {busy && !session ? (
          <div className="loading-card">
            <span className="loader" /> Loading game...
          </div>
        ) : (
          <div className="games-layout">
            <aside className="games-sidebar">
              <div className="game-side-card">
                <h2>{copy.chooseCharacter}</h2>
                <div className="character-list">
                  {characters.map((character) => (
                    <button
                      key={character.id}
                      className={
                        selectedCharacter?.id === character.id ? "active" : ""
                      }
                      onClick={() => changeCharacter(character)}
                    >
                      <span
                        className="character-token"
                        style={{ background: character.color_primary }}
                      >
                        <UserRound size={19} />
                      </span>
                      <strong>{character.name}</strong>
                      <small>{roleLabel[language][character.role]}</small>
                    </button>
                  ))}
                </div>
              </div>

              <div className="game-side-card">
                <h2>{copy.chooseScenario}</h2>
                <p className="game-auto-note">{copy.auto}</p>
                <div className="scenario-list compact">
                  {scenarios.map((scenario) => (
                    <button
                      key={scenario.id}
                      className={
                        selectedScenario?.id === scenario.id ? "active" : ""
                      }
                      onClick={() => changeScenario(scenario)}
                    >
                      <strong>{scenario.title}</strong>
                      <small>{scenario.description}</small>
                    </button>
                  ))}
                </div>
              </div>

              <div className="game-side-card leaderboard-mini">
                <h2>{copy.leaderboard}</h2>
                {leaderboard.slice(0, 5).map((entry) => (
                  <div key={entry.rank}>
                    <span>#{entry.rank}</span>
                    <strong>{entry.user_name}</strong>
                    <small>{entry.total_score}</small>
                  </div>
                ))}
                {leaderboard.length === 0 && <p>{copy.noScores}</p>}
              </div>
            </aside>

            <div className="game3d-shell">
              <div className="game3d-hud">
                <div>
                  <span>{copy.mission}</span>
                  <strong>
                    {session?.mission_title ||
                      selectedScenario?.title ||
                      "Cyber mission"}
                  </strong>
                </div>
                <div>
                  <span>{copy.score}</span>
                  <strong>{session?.score || 0}</strong>
                </div>
                <div>
                  <span>{copy.step}</span>
                  <strong>
                    {session ? `${stepIndex + 1}/${session.steps.length}` : "—"}
                  </strong>
                </div>
                {session && (
                  <div>
                    <span>{copy.difficulty}</span>
                    <strong>{difficultyLabel[language][session.difficulty]}</strong>
                  </div>
                )}
              </div>

              <div className="game3d-task-panel">
                <span>{copy.currentTask}</span>
                <strong>{currentStep?.prompt || copy.startHint}</strong>
              </div>

              <div className="game3d-canvas-wrap">
                <GameCanvas
                  key={`${session?.id || "preview"}-${stepIndex}-${result ? "done" : "active"}`}
                  character={selectedCharacter}
                  step={currentStep}
                  sceneKey={session?.scene_key || "cyber_office"}
                  disabled={busy || Boolean(result)}
                  onSelect={session ? selectObject : () => undefined}
                />
              </div>

              {!session && (
                <div className="game3d-start-panel">
                  <h2>{selectedScenario?.title}</h2>
                  <p>{selectedScenario?.description}</p>
                  <button
                    className="button button-primary"
                    onClick={startMission}
                    disabled={!selectedCharacter || !selectedScenario || busy}
                  >
                    <Play size={17} /> {copy.start}
                  </button>
                </div>
              )}

              {feedback && (
                <div
                  className={
                    feedback.correct
                      ? "game3d-feedback correct"
                      : "game3d-feedback wrong"
                  }
                >
                  {feedback.correct ? <ShieldCheck /> : <Award />}
                  <div>
                    <strong>
                      {feedback.correct ? copy.correct : copy.wrong}{" "}
                      {feedback.points_delta > 0 ? "+" : ""}
                      {feedback.points_delta}
                    </strong>
                    <p>{feedback.feedback}</p>
                  </div>
                </div>
              )}

              {result && (
                <div className="game3d-result">
                  <span className="game3d-result-icon">
                    <Trophy />
                  </span>
                  <div>
                    <h2>{copy.completed}</h2>
                    <p>
                      {result.mission_title} ·{" "}
                      {difficultyLabel[language][result.difficulty]}
                    </p>
                  </div>
                  <strong>{result.score_percent}%</strong>
                  <p>
                    {result.score}/{result.max_score} · +{result.points_awarded}{" "}
                    {copy.points}
                  </p>
                  {!user && (
                    <Link className="button button-primary" href="/login?next=/games">
                      {copy.loginCta} <ArrowRight size={17} />
                    </Link>
                  )}
                  <button className="button button-ghost" onClick={reset}>
                    <RotateCcw size={17} /> {copy.again}
                  </button>
                  <button
                    className="button button-primary"
                    onClick={() => {
                      reset();
                      window.setTimeout(() => {
                        void startMission();
                      }, 0);
                    }}
                  >
                    <Play size={17} /> {copy.start}
                  </button>
                </div>
              )}

              {result && (
                <div className="game3d-review-panel">
                  <h2>{copy.review}</h2>
                  {result.turns.map((turn) => (
                    <article
                      key={turn.step}
                      className={turn.correct ? "correct" : "wrong"}
                    >
                      <span className="review-step">{turn.step}</span>
                      <div>
                        <h3>{turn.prompt}</h3>
                        <p>
                          <strong>{copy.selected}</strong> {turn.selected_label}
                        </p>
                        {!turn.correct && (
                          <p>
                            <strong>{copy.expected}</strong> {turn.correct_label}
                          </p>
                        )}
                        <p>{turn.feedback}</p>
                      </div>
                      <strong className="review-points">
                        {turn.points_delta > 0 ? "+" : ""}
                        {turn.points_delta}
                      </strong>
                      {turn.correct ? <CheckCircle2 /> : <XCircle />}
                    </article>
                  ))}
                </div>
              )}

              {error && <div className="form-error">{error}</div>}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
