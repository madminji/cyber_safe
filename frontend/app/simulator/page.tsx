"use client";

import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  LockKeyhole,
  MessageCircleWarning,
  RotateCcw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { GameResult, GameScenario, GameState } from "@/lib/types";

type AnswerResponse = {
  feedback: string;
  choice_points: number;
  completed: boolean;
  session: GameState;
};

const difficultyLabels = {
  easy: "Легко",
  medium: "Средне",
  hard: "Сложно",
};

export default function SimulatorPage() {
  const { user, loading, reloadUser } = useAuth();
  const { language } = useLanguage();
  const [scenarios, setScenarios] = useState<GameScenario[]>([]);
  const [game, setGame] = useState<GameState | null>(null);
  const [result, setResult] = useState<GameResult | null>(null);
  const [feedback, setFeedback] = useState("");
  const [feedbackPositive, setFeedbackPositive] = useState(true);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setBusy(true);
    api<GameScenario[]>(`/game/scenarios/?language=${language}`)
      .then(setScenarios)
      .catch((requestError) => setError(requestError.message))
      .finally(() => setBusy(false));
  }, [language]);

  const start = async (scenario: GameScenario) => {
    if (!user) return;
    setBusy(true);
    setError("");
    setResult(null);
    setFeedback("");
    try {
      setGame(
        await api<GameState>("/game/sessions/", {
          method: "POST",
          auth: true,
          body: JSON.stringify({
            scenario_id: scenario.id,
            language,
          }),
        }),
      );
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const answer = async (choiceId: string) => {
    if (!game) return;
    setBusy(true);
    setError("");
    try {
      const response = await api<AnswerResponse>(
        `/game/sessions/${game.id}/answer/`,
        {
          method: "POST",
          auth: true,
          body: JSON.stringify({ choice_id: choiceId }),
        },
      );
      setFeedback(response.feedback);
      setFeedbackPositive(response.choice_points > 0);
      setGame(response.session);
      if (response.completed) {
        const completedResult = await api<GameResult>(
          `/game/sessions/${game.id}/result/`,
          { auth: true },
        );
        setResult(completedResult);
        await reloadUser();
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setGame(null);
    setResult(null);
    setFeedback("");
    setError("");
  };

  if (result) {
    const level = {
      expert: {
        title: "Атаку отражено",
        text: "Вы распознали давление и не передали контроль мошеннику.",
        icon: <ShieldCheck />,
      },
      resistant: {
        title: "Хорошая устойчивость",
        text: "Большинство уловок распознано, но несколько решений были рискованными.",
        icon: <BrainCircuit />,
      },
      vulnerable: {
        title: "Нужна практика",
        text: "Некоторые манипуляции сработали. Разберите диалог перед новой попыткой.",
        icon: <AlertTriangle />,
      },
    }[result.level];

    return (
      <section className="page-section simulator-page">
        <div className="container simulator-container">
          <div className={`game-result-card ${result.level}`}>
            <span className="game-result-icon">{level.icon}</span>
            <span className="eyebrow">Симуляция завершена</span>
            <h1>{level.title}</h1>
            <div className="game-score">{result.score_percent}%</div>
            <p>{level.text}</p>
            <strong>+{result.points_awarded} баллов защиты</strong>
            <button className="button button-primary" onClick={reset}>
              <RotateCcw size={17} /> Другой сценарий
            </button>
          </div>

          <div className="game-review">
            <h2>Разбор диалога</h2>
            {result.ai_analysis && (
              <div className="ai-coach-card">
                <span>
                  <Sparkles size={17} /> AI-разбор
                </span>
                <p>{result.ai_analysis}</p>
                <small>Модель: {result.ai_model}</small>
              </div>
            )}
            {result.turns.map((turn) => (
              <article key={turn.step}>
                <div className="review-step">{turn.step}</div>
                <div>
                  <span className="tactic-label">{turn.tactic}</span>
                  <p className="scammer-line">{turn.message}</p>
                  <p>
                    <strong>Ваш ответ:</strong> {turn.answer}
                  </p>
                  <p className="turn-feedback">{turn.feedback}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (game) {
    const progress = game.step_number
      ? Math.round((game.step_number / game.total_steps) * 100)
      : 100;
    return (
      <section className="page-section simulator-page">
        <div className="container simulator-container">
          <button className="back-button game-back" onClick={reset}>
            <ArrowLeft size={17} /> Выбрать другой сценарий
          </button>
          <div className="game-shell">
            <div className="game-header">
              <div>
                <span className="live-dot" />
                Симуляция: {game.scenario_title}
              </div>
              <span>
                Ход {game.step_number} из {game.total_steps}
              </span>
            </div>
            <div className="progress-track game-progress">
              <span style={{ width: `${progress}%` }} />
            </div>

            <div className="chat-stage">
              <div className="caller-avatar">
                <Bot size={32} />
              </div>
              <div className="scammer-message">
                <small>Неизвестный собеседник</small>
                <p>{game.message}</p>
              </div>
            </div>

            {feedback && (
              <div
                className={
                  feedbackPositive
                    ? "game-feedback positive"
                    : "game-feedback negative"
                }
              >
                {feedbackPositive ? <CheckCircle2 /> : <AlertTriangle />}
                <p>{feedback}</p>
              </div>
            )}

            <div className="game-choices">
              <span>Как вы ответите?</span>
              {game.choices.map((choice) => (
                <button
                  key={choice.id}
                  disabled={busy}
                  onClick={() => answer(choice.id)}
                >
                  <span>{String.fromCharCode(64 + choice.order)}</span>
                  {choice.text}
                  <ArrowRight size={17} />
                </button>
              ))}
            </div>
            {error && <div className="form-error">{error}</div>}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="page-section simulator-page">
      <div className="container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <Sparkles size={15} /> Безопасная тренировка
          </span>
          <h1>Симулятор мошеннических атак</h1>
          <p>
            Пройдите реалистичный диалог и проверьте, сможете ли вы распознать
            давление до передачи денег или секретных данных.
          </p>
        </div>

        {!loading && !user ? (
          <div className="empty-state">
            <span className="empty-icon">
              <LockKeyhole />
            </span>
            <h2>Для симуляции нужен вход</h2>
            <p>Результаты и баллы сохраняются в личном кабинете.</p>
            <Link className="button button-primary" href="/login">
              Войти
            </Link>
          </div>
        ) : busy ? (
          <div className="loading-card">
            <span className="loader" /> Загружаем сценарии...
          </div>
        ) : (
          <div className="scenario-grid">
            {scenarios.map((scenario, index) => (
              <article className="scenario-card" key={scenario.id}>
                <div className={`scenario-visual scenario-${index + 1}`}>
                  {scenario.scam_type === "malware" ? (
                    <MessageCircleWarning />
                  ) : (
                    <Bot />
                  )}
                  <span>{scenario.steps_count} хода</span>
                </div>
                <div>
                  <span className="scenario-difficulty">
                    {difficultyLabels[scenario.difficulty]}
                  </span>
                  <h2>{scenario.title}</h2>
                  <p>{scenario.description}</p>
                  <button
                    className="button button-primary button-wide"
                    onClick={() => start(scenario)}
                  >
                    Начать симуляцию <ArrowRight size={17} />
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
        {error && <div className="form-error centered">{error}</div>}
      </div>
    </section>
  );
}
