"use client";

import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Globe2,
  LockKeyhole,
  MessageCircleWarning,
  PhoneCall,
  PhoneOff,
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
import { TranslationKey } from "@/lib/translations";

type AnswerResponse = {
  feedback: string;
  choice_points: number;
  completed: boolean;
  session: GameState;
};

type ChatMessage = {
  id: string;
  role: "npc" | "user";
  text: string;
};

export default function SimulatorPage() {
  const { user, loading, reloadUser } = useAuth();
  const { language, t } = useLanguage();
  const [scenarios, setScenarios] = useState<GameScenario[]>([]);
  const [game, setGame] = useState<GameState | null>(null);
  const [result, setResult] = useState<GameResult | null>(null);
  const [feedback, setFeedback] = useState("");
  const [feedbackPositive, setFeedbackPositive] = useState(true);
  const [customAnswer, setCustomAnswer] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
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
    setCustomAnswer("");
    setChatMessages([]);
    try {
      const started = await api<GameState>("/game/sessions/", {
        method: "POST",
        auth: true,
        body: JSON.stringify({
          scenario_id: scenario.id,
          language,
        }),
      });
      setGame(started);
      if (started.message) {
        setChatMessages([
          {
            id: `${started.id}-npc-${started.step_number || 1}`,
            role: "npc",
            text: started.message,
          },
        ]);
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const answer = async () => {
    if (!game) return;
    const freeText = customAnswer.trim();
    if (freeText.length < 2) {
      setError("Напишите ответ или выберите одну из готовых стратегий.");
      return;
    }
    setBusy(true);
    setError("");
    const userMessage: ChatMessage = {
      id: `${game.id}-user-${Date.now()}`,
      role: "user",
      text: freeText,
    };
    setChatMessages((current) => [...current, userMessage]);
    setCustomAnswer("");
    try {
      const response = await api<AnswerResponse>(
        `/game/sessions/${game.id}/answer/`,
        {
          method: "POST",
          auth: true,
          body: JSON.stringify({
            custom_text: freeText,
          }),
        },
      );
      setFeedback(response.feedback);
      setFeedbackPositive(response.choice_points > 0);
      setGame(response.session);
      if (!response.completed && response.session.message) {
        setChatMessages((current) => [
          ...current,
          {
            id: `${response.session.id}-npc-${response.session.step_number || Date.now()}`,
            role: "npc",
            text: response.session.message || "",
          },
        ]);
      }
      if (response.completed) {
        const completedResult = await api<GameResult>(
          `/game/sessions/${game.id}/result/`,
          { auth: true },
        );
        setResult(completedResult);
        await reloadUser();
      }
    } catch (requestError) {
      setChatMessages((current) =>
        current.filter((message) => message.id !== userMessage.id),
      );
      setCustomAnswer(freeText);
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setGame(null);
    setResult(null);
    setFeedback("");
    setCustomAnswer("");
    setChatMessages([]);
    setError("");
  };

  const difficultyLabels = {
    easy: t("common.easy"),
    medium: t("common.medium"),
    hard: t("common.hard"),
  };

  if (result) {
    const level = {
      expert: {
        title: t("sim.expertTitle"),
        text: t("sim.expertText"),
        icon: <ShieldCheck />,
      },
      resistant: {
        title: t("sim.resistantTitle"),
        text: t("sim.resistantText"),
        icon: <BrainCircuit />,
      },
      vulnerable: {
        title: t("sim.vulnerableTitle"),
        text: t("sim.vulnerableText"),
        icon: <AlertTriangle />,
      },
    }[result.level];

    return (
      <section className="page-section simulator-page">
        <div className="container simulator-container">
          <div className={`game-result-card ${result.level}`}>
            <span className="game-result-icon">{level.icon}</span>
            <span className="eyebrow">{t("sim.completed")}</span>
            <h1>{level.title}</h1>
            <div className="game-score">{result.score_percent}%</div>
            <p>{level.text}</p>
            <strong>
              +{result.points_awarded} {t("sim.points")}
            </strong>
            <button className="button button-primary" onClick={reset}>
              <RotateCcw size={17} /> {t("sim.other")}
            </button>
          </div>

          <div className="game-review">
            <h2>{t("sim.review")}</h2>
            {result.ai_analysis && (
              <div className="ai-coach-card">
                <span>
                  <Sparkles size={17} /> {t("sim.aiReview")}
                </span>
                <p>{result.ai_analysis}</p>
                <small>
                  {t("sim.model")}: {result.ai_model}
                </small>
              </div>
            )}
            {result.turns.map((turn) => (
              <article key={turn.step}>
                <div className="review-step">{turn.step}</div>
                <div>
                  <span className="tactic-label">{turn.tactic}</span>
                  <p className="scammer-line">{turn.message}</p>
                  <p>
                    <strong>{t("sim.yourAnswer")}</strong> {turn.answer}
                  </p>
                  {turn.selected_safe_intent !== turn.answer && (
                    <p className="turn-intent">
                      <strong>{t("sim.selectedIntent")}</strong>{" "}
                      {turn.selected_safe_intent}
                    </p>
                  )}
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
            <ArrowLeft size={17} /> {t("sim.chooseOther")}
          </button>
          <div className="game-shell">
            <div className="game-header">
              <div>
                <span className="live-dot" />
                {t("sim.simulation")}: {game.scenario_title}
              </div>
              <span>
                {t("sim.step", {
                  current: game.step_number || 0,
                  total: game.total_steps,
                })}
              </span>
            </div>
            <div className="progress-track game-progress">
              <span style={{ width: `${progress}%` }} />
            </div>

            {game.interface_type === "call" ? (
              <div className="call-stage">
                <div className="call-pulse">
                  <PhoneCall size={42} />
                </div>
                <small>{t("sim.incomingCall")}</small>
                <h2>{t("sim.callerUnknown")}</h2>
                <span>+998 •• ••• •• ••</span>
                <p>{game.message}</p>
                <div className="call-security-note">
                  <ShieldCheck size={15} /> {t("sim.secureNotice")}
                </div>
                <button
                  type="button"
                  className="hangup-button"
                  aria-label={t("sim.chooseOther")}
                  onClick={reset}
                >
                  <PhoneOff />
                </button>
              </div>
            ) : game.interface_type === "website" ? (
              <div className="website-stage">
                <div className="fake-browser-bar">
                  <span />
                  <span />
                  <span />
                  <div>
                    <Globe2 size={14} /> payme-secure-check.example
                  </div>
                </div>
                <div className="website-warning">
                  <AlertTriangle size={17} /> {t("sim.browserWarning")}
                </div>
                <div className="fake-website-card">
                  <ShieldCheck size={38} />
                  <h2>{game.scenario_title}</h2>
                  <p>{game.message}</p>
                </div>
              </div>
            ) : (
              <div className="messenger-stage">
                <div className="messenger-topbar">
                  <div className="caller-avatar">
                    <Bot size={28} />
                  </div>
                  <div>
                    <strong>{t("sim.unknown")}</strong>
                    <small>online</small>
                  </div>
                </div>
                <div className="chat-stage realistic-chat-stage">
                  {chatMessages.map((message) => (
                    <div
                      className={
                        message.role === "user"
                          ? "chat-bubble user-bubble"
                          : "chat-bubble npc-bubble"
                      }
                      key={message.id}
                    >
                      {message.role === "npc" && <small>Telegram</small>}
                      <p>{message.text}</p>
                    </div>
                  ))}
                  {busy && (
                    <div className="typing-indicator">
                      <span />
                      <span />
                      <span />
                    </div>
                  )}
                </div>
              </div>
            )}

            {feedback && false && (
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
              <span>Ваш ответ</span>
              <label className="custom-answer-box">
                <textarea
                  value={customAnswer}
                  onChange={(event) => setCustomAnswer(event.target.value)}
                  maxLength={600}
                  disabled={busy}
                  placeholder="Напишите сообщение собеседнику..."
                  rows={3}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      answer();
                    }
                  }}
                />
              </label>
              <button
                className="button button-primary button-wide"
                disabled={busy || customAnswer.trim().length < 2}
                onClick={answer}
              >
                {busy ? "Отправляем..." : "Отправить"} <ArrowRight size={17} />
              </button>
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
            <Sparkles size={15} /> {t("sim.eyebrow")}
          </span>
          <h1>{t("sim.title")}</h1>
          <p>{t("sim.lead")}</p>
        </div>

        {!loading && !user ? (
          <div className="empty-state">
            <span className="empty-icon">
              <LockKeyhole />
            </span>
            <h2>{t("sim.loginTitle")}</h2>
            <p>{t("sim.loginText")}</p>
            <Link className="button button-primary" href="/login">
              {t("common.login")}
            </Link>
          </div>
        ) : busy ? (
          <div className="loading-card">
            <span className="loader" /> {t("sim.loading")}
          </div>
        ) : (
          <div className="scenario-grid">
            {scenarios.map((scenario, index) => (
              <article className="scenario-card" key={scenario.id}>
                <div className={`scenario-visual scenario-${index + 1}`}>
                  {scenario.interface_type === "call" ? (
                    <PhoneCall />
                  ) : scenario.interface_type === "website" ? (
                    <Globe2 />
                  ) : scenario.scam_type === "malware" ? (
                    <MessageCircleWarning />
                  ) : (
                    <Bot />
                  )}
                  <span>
                    {scenario.steps_count} {t("sim.steps")}
                  </span>
                </div>
                <div>
                  <span className="scenario-interface">
                    {t(
                      `sim.mode.${scenario.interface_type}` as TranslationKey,
                    )}
                  </span>
                  <span className="scenario-difficulty">
                    {difficultyLabels[scenario.difficulty]}
                  </span>
                  <h2>{scenario.title}</h2>
                  <p>{scenario.description}</p>
                  <button
                    className="button button-primary button-wide"
                    onClick={() => start(scenario)}
                  >
                    {t("sim.start")} <ArrowRight size={17} />
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
