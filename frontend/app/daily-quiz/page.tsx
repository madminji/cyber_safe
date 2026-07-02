"use client";

import {
  ArrowLeft,
  ArrowRight,
  CalendarCheck2,
  Check,
  Flame,
  LockKeyhole,
  Trophy,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import {
  DailyQuizStatus,
  QuizResult,
  QuizSession,
} from "@/lib/types";

export default function DailyQuizPage() {
  const { user, loading, reloadUser } = useAuth();
  const { language, t } = useLanguage();
  const [status, setStatus] = useState<DailyQuizStatus | null>(null);
  const [session, setSession] = useState<QuizSession | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [current, setCurrent] = useState(0);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [startedAt, setStartedAt] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadStatus = async () => {
    if (!user) return;
    setStatus(await api<DailyQuizStatus>("/quiz/daily/", { auth: true }));
  };

  useEffect(() => {
    if (!loading && user) {
      loadStatus().catch((requestError) => setError(requestError.message));
    }
  }, [loading, user]);

  const start = async () => {
    setBusy(true);
    setError("");
    try {
      const data = await api<QuizSession & { completed?: boolean; score?: number }>(
        "/quiz/daily/",
        {
          method: "POST",
          auth: true,
          body: JSON.stringify({ language }),
        },
      );
      if (data.completed) {
        await loadStatus();
        return;
      }
      setSession(data);
      setAnswers({});
      setCurrent(0);
      setStartedAt(Date.now());
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const submit = async () => {
    if (!session) return;
    setBusy(true);
    setError("");
    try {
      const completed = await api<QuizResult>(
        `/quiz/sessions/${session.session_id}/submit/`,
        {
          method: "POST",
          auth: true,
          body: JSON.stringify({
            answers: session.questions.map((question) => ({
              question_id: question.id,
              choice_id: answers[question.id],
            })),
            duration_seconds: Math.max(
              1,
              Math.round((Date.now() - startedAt) / 1000),
            ),
          }),
        },
      );
      setResult(completed);
      setSession(null);
      await Promise.all([loadStatus(), reloadUser()]);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" />
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <LockKeyhole />
          <h1>{t("daily.loginTitle")}</h1>
          <p>{t("daily.loginText")}</p>
          <Link className="button button-primary" href="/login?next=/daily-quiz">
            {t("common.login")}
          </Link>
        </div>
      </section>
    );
  }

  if (session) {
    const question = session.questions[current];
    const selected = answers[question.id];
    const allAnswered =
      Object.keys(answers).length === session.question_count;
    return (
      <section className="page-section quiz-page daily-quiz-page">
        <div className="container quiz-container">
          <div className="quiz-topline">
            <div>
              <span className="eyebrow">
                <CalendarCheck2 size={16} /> {t("daily.eyebrow")}
              </span>
              <h1>{t("daily.title")}</h1>
            </div>
            <span className="question-counter">
              {current + 1} / {session.question_count}
            </span>
          </div>
          <div className="progress-track">
            <span
              style={{
                width: `${((current + 1) / session.question_count) * 100}%`,
              }}
            />
          </div>
          <div className="question-card">
            <h2>{question.text}</h2>
            <div className="choice-list">
              {question.choices.map((choice, index) => (
                <button
                  key={choice.id}
                  className={selected === choice.id ? "choice selected" : "choice"}
                  onClick={() =>
                    setAnswers((currentAnswers) => ({
                      ...currentAnswers,
                      [question.id]: choice.id,
                    }))
                  }
                >
                  <span>{String.fromCharCode(65 + index)}</span>
                  {choice.text}
                  <i>{selected === choice.id && <Check size={17} />}</i>
                </button>
              ))}
            </div>
            <div className="quiz-navigation">
              <button
                className="button button-ghost"
                disabled={current === 0}
                onClick={() => setCurrent((value) => value - 1)}
              >
                <ArrowLeft size={17} /> {t("quiz.back")}
              </button>
              {current < session.question_count - 1 ? (
                <button
                  className="button button-primary"
                  disabled={!selected}
                  onClick={() => setCurrent((value) => value + 1)}
                >
                  {t("quiz.next")} <ArrowRight size={17} />
                </button>
              ) : (
                <button
                  className="button button-primary"
                  disabled={!allAnswered || busy}
                  onClick={submit}
                >
                  {busy ? t("quiz.checking") : t("quiz.finish")}
                </button>
              )}
            </div>
          </div>
        </div>
      </section>
    );
  }

  const completed = result || status?.completed;
  const score = result?.score ?? status?.score;
  return (
    <section className="page-section daily-quiz-page">
      <div className="container narrow-container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <CalendarCheck2 size={16} /> {t("daily.eyebrow")}
          </span>
          <h1>{t("daily.title")}</h1>
          <p>{t("daily.lead")}</p>
        </div>
        <div className="daily-stats">
          <article>
            <Flame />
            <strong>{status?.streak || 0}</strong>
            <span>
              {t("daily.streak")} · {t("daily.days")}
            </span>
          </article>
          <article>
            <Trophy />
            <strong>{status?.total_completed || 0}</strong>
            <span>{t("daily.total")}</span>
          </article>
        </div>
        <div className="daily-action-card">
          {completed ? (
            <>
              <CheckCircle2Icon />
              <h2>{t("daily.completed")}</h2>
              <strong className="daily-score">
                {t("daily.score")}: {score}%
              </strong>
              <p>{t("daily.tomorrow")}</p>
              {result && (
                <div className="daily-review">
                  {result.answers.map((answer, index) => (
                    <div
                      key={answer.question_id}
                      className={answer.is_correct ? "correct" : "wrong"}
                    >
                      <strong>
                        {t("quiz.question", { number: index + 1 })}:{" "}
                        {answer.is_correct
                          ? t("quiz.correct")
                          : t("quiz.incorrect")}
                      </strong>
                      <p>{answer.explanation}</p>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <>
              <CalendarCheck2 />
              <h2>{t("daily.title")}</h2>
              <p>{t("daily.lead")}</p>
              <button className="button button-primary" onClick={start} disabled={busy}>
                {status?.started ? t("daily.continue") : t("daily.start")}
                <ArrowRight size={17} />
              </button>
            </>
          )}
          {error && <div className="form-error">{error}</div>}
        </div>
      </div>
    </section>
  );
}

function CheckCircle2Icon() {
  return <CalendarCheck2 size={54} />;
}
