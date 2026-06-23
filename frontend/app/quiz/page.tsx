"use client";

import {
  ArrowLeft,
  ArrowRight,
  Award,
  Check,
  CircleAlert,
  RotateCcw,
  X,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { QuizResult, QuizSession } from "@/lib/types";

type SelectedAnswers = Record<string, string>;

export default function QuizPage() {
  const { language } = useLanguage();
  const [session, setSession] = useState<QuizSession | null>(null);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<SelectedAnswers>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [startedAt, setStartedAt] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const initialRequestStarted = useRef(false);

  const question = session?.questions[current];
  const progress = session
    ? Math.round(((current + 1) / session.question_count) * 100)
    : 0;

  const start = async () => {
    setBusy(true);
    setError("");
    try {
      const data = await api<QuizSession>("/quiz/sessions/", {
        method: "POST",
        auth: true,
        body: JSON.stringify({ language }),
      });
      setSession(data);
      setCurrent(0);
      setAnswers({});
      setResult(null);
      setStartedAt(Date.now());
      setError("");
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (initialRequestStarted.current) return;
    initialRequestStarted.current = true;
    start();
    // The user can restart explicitly after switching the interface language.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selected = question ? answers[question.id] : undefined;
  const answeredCount = Object.keys(answers).length;
  const canSubmit = session && answeredCount === session.question_count;

  const submit = async () => {
    if (!session || !canSubmit) return;
    setBusy(true);
    setError("");
    try {
      const data = await api<QuizResult>(
        `/quiz/sessions/${session.session_id}/submit/`,
        {
          method: "POST",
          auth: true,
          body: JSON.stringify({
            answers: session.questions.map((item) => ({
              question_id: item.id,
              choice_id: answers[item.id],
            })),
            duration_seconds: Math.max(
              1,
              Math.round((Date.now() - startedAt) / 1000),
            ),
          }),
        },
      );
      setResult(data);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const levelLabel = useMemo(
    () =>
      ({
        none: "Попробуйте ещё раз",
        basic: "Базовый",
        advanced: "Продвинутый",
        expert: "Эксперт",
      })[result?.level || "none"],
    [result],
  );

  if (result) {
    return (
      <section className="page-section quiz-page">
        <div className="container narrow-container">
          <div className="result-card">
            <div className={`score-ring ${result.passed ? "passed" : "failed"}`}>
              <span>{result.score}</span>
              <small>%</small>
            </div>
            <span className="eyebrow">Тест завершён</span>
            <h1>{levelLabel}</h1>
            <p>
              {result.passed
                ? "Отличная работа. Вы умеете замечать основные признаки цифрового мошенничества."
                : "Некоторые уловки всё ещё опасны. Разберите ответы и попробуйте снова."}
            </p>
            <div className="result-actions">
              {result.certificate_id && (
                <Link
                  className="button button-primary"
                  href="/certificates"
                >
                  <Award size={18} /> Открыть сертификат
                </Link>
              )}
              <button className="button button-ghost" onClick={start}>
                <RotateCcw size={17} /> Пройти снова
              </button>
            </div>
          </div>

          <div className="answers-review">
            <h2>Разбор ответов</h2>
            {result.answers.map((answer, index) => (
              <article
                key={answer.question_id}
                className={answer.is_correct ? "review correct" : "review wrong"}
              >
                <span className="review-icon">
                  {answer.is_correct ? <Check /> : <X />}
                </span>
                <div>
                  <strong>
                    Вопрос {index + 1}:{" "}
                    {answer.is_correct ? "верно" : "есть ошибка"}
                  </strong>
                  <p>{answer.explanation}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="page-section quiz-page">
      <div className="container quiz-container">
        <div className="quiz-topline">
          <div>
            <span className="eyebrow">Диагностика знаний</span>
            <h1>Тест по цифровой безопасности</h1>
          </div>
          {session && (
            <span className="question-counter">
              {current + 1} / {session.question_count}
            </span>
          )}
        </div>
        {session && (
          <div className="progress-track">
            <span style={{ width: `${progress}%` }} />
          </div>
        )}

        {busy && !session ? (
          <div className="loading-card">
            <span className="loader" />
            Формируем персональный набор вопросов...
          </div>
        ) : question ? (
          <div className="question-card">
            <div className="question-meta">
              <span>{question.category.replaceAll("_", " ")}</span>
              <span>{question.difficulty}</span>
            </div>
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
            {error && (
              <div className="form-error">
                <CircleAlert size={17} /> {error}
              </div>
            )}
            <div className="quiz-navigation">
              <button
                className="button button-ghost"
                disabled={current === 0}
                onClick={() => setCurrent((value) => value - 1)}
              >
                <ArrowLeft size={17} /> Назад
              </button>
              {session && current < session.question_count - 1 ? (
                <button
                  className="button button-primary"
                  disabled={!selected}
                  onClick={() => setCurrent((value) => value + 1)}
                >
                  Далее <ArrowRight size={17} />
                </button>
              ) : (
                <button
                  className="button button-primary"
                  disabled={!canSubmit || busy}
                  onClick={submit}
                >
                  {busy ? "Проверяем..." : "Завершить тест"}
                  <ArrowRight size={17} />
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="loading-card error-state">
            <CircleAlert />
            <p>{error || "Не удалось загрузить вопросы."}</p>
            <button className="button button-primary" onClick={start}>
              Повторить
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
