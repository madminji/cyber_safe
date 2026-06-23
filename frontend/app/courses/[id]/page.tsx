"use client";

import {
  ArrowLeft,
  ArrowRight,
  BookOpenCheck,
  Check,
  CheckCircle2,
  Clock3,
  LockKeyhole,
  PlayCircle,
  X,
} from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { CourseDetail, LessonDetail } from "@/lib/types";

type AnswerResult = {
  correct: boolean;
  completed: boolean;
  completed_now: boolean;
  explanation: string;
};

export default function CourseDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user, loading, reloadUser } = useAuth();
  const { language } = useLanguage();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [selectedChoice, setSelectedChoice] = useState("");
  const [answerResult, setAnswerResult] = useState<AnswerResult | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  const loadCourse = useCallback(async () => {
    if (!params.id || loading) return;
    setBusy(true);
    try {
      setCourse(
        await api<CourseDetail>(
          `/courses/${params.id}/?language=${language}`,
          { auth: Boolean(user) },
        ),
      );
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  }, [language, loading, params.id, user]);

  useEffect(() => {
    loadCourse();
  }, [loadCourse]);

  const openLesson = async (lessonId: string) => {
    if (!user) {
      router.push("/login");
      return;
    }
    setBusy(true);
    setError("");
    setAnswerResult(null);
    setSelectedChoice("");
    try {
      setLesson(
        await api<LessonDetail>(
          `/courses/lessons/${lessonId}/?language=${language}`,
          { auth: true },
        ),
      );
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const submitAnswer = async () => {
    if (!lesson || !selectedChoice) return;
    setBusy(true);
    try {
      const result = await api<AnswerResult>(
        `/courses/lessons/${lesson.id}/answer/`,
        {
          method: "POST",
          auth: true,
          body: JSON.stringify({ choice_id: selectedChoice }),
        },
      );
      setAnswerResult(result);
      if (result.correct) {
        setLesson({ ...lesson, completed: true });
        await Promise.all([loadCourse(), reloadUser()]);
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  if (busy && !course) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" /> Открываем курс...
        </div>
      </section>
    );
  }

  if (!course) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <h1>Курс не найден</h1>
          <p>{error}</p>
          <Link href="/courses" className="button button-primary">
            Вернуться к курсам
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="page-section course-detail-page">
      <div className="container">
        <Link href="/courses" className="back-link">
          <ArrowLeft size={17} /> Все курсы
        </Link>
        <div className="course-detail-hero">
          <div>
            <span className="eyebrow">{course.level}</span>
            <h1>{course.title}</h1>
            <p>{course.description}</p>
            <div className="course-detail-meta">
              <span>
                <BookOpenCheck size={17} /> {course.lessons_count} урока
              </span>
              <span>
                <Clock3 size={17} /> {course.duration_minutes} минут
              </span>
            </div>
          </div>
          <div className="course-progress-orb">
            <strong>{course.progress_percent}%</strong>
            <span>пройдено</span>
          </div>
        </div>

        <div className="lesson-list">
          {course.lessons.map((item) => (
            <button
              className={item.completed ? "lesson-row completed" : "lesson-row"}
              key={item.id}
              onClick={() => openLesson(item.id)}
            >
              <span className="lesson-order">
                {item.completed ? <Check size={18} /> : item.order}
              </span>
              <div>
                <strong>{item.title}</strong>
                <p>{item.summary}</p>
              </div>
              <span className="lesson-duration">
                <Clock3 size={14} /> {item.duration_minutes} мин
              </span>
              {user ? <PlayCircle /> : <LockKeyhole />}
            </button>
          ))}
        </div>

        {!user && (
          <div className="course-login-callout">
            <LockKeyhole />
            <div>
              <strong>Войдите, чтобы открыть уроки</strong>
              <p>Прогресс и баллы сохраняются в личном кабинете.</p>
            </div>
            <Link href="/login" className="button button-primary button-small">
              Войти
            </Link>
          </div>
        )}

        {lesson && (
          <div className="lesson-modal" onMouseDown={() => setLesson(null)}>
            <article
              className="lesson-reader"
              onMouseDown={(event) => event.stopPropagation()}
            >
              <button className="modal-close" onClick={() => setLesson(null)}>
                ×
              </button>
              <div className="lesson-reader-head">
                <span className="eyebrow">Урок {lesson.order}</span>
                <h2>{lesson.title}</h2>
                <p>{lesson.summary}</p>
              </div>
              {lesson.video_url && (
                <video className="lesson-video" controls src={lesson.video_url} />
              )}
              <div className="lesson-content">
                {lesson.content.split("\n").map((paragraph, index) =>
                  paragraph ? <p key={index}>{paragraph}</p> : <br key={index} />,
                )}
              </div>

              {lesson.question && (
                <div className="lesson-checkpoint">
                  <span className="eyebrow">Проверьте себя</span>
                  <h3>{lesson.question.text}</h3>
                  <div className="lesson-choices">
                    {lesson.question.choices.map((choice) => (
                      <button
                        key={choice.id}
                        className={
                          selectedChoice === choice.id ? "selected" : ""
                        }
                        onClick={() => {
                          setSelectedChoice(choice.id);
                          setAnswerResult(null);
                        }}
                      >
                        <span>{String.fromCharCode(64 + choice.order)}</span>
                        {choice.text}
                      </button>
                    ))}
                  </div>
                  {answerResult && (
                    <div
                      className={
                        answerResult.correct
                          ? "checkpoint-result correct"
                          : "checkpoint-result wrong"
                      }
                    >
                      {answerResult.correct ? <CheckCircle2 /> : <X />}
                      <div>
                        <strong>
                          {answerResult.correct
                            ? "Урок завершён"
                            : "Попробуйте ещё раз"}
                        </strong>
                        <p>{answerResult.explanation}</p>
                      </div>
                    </div>
                  )}
                  {!lesson.completed && (
                    <button
                      className="button button-primary button-wide"
                      disabled={!selectedChoice || busy}
                      onClick={submitAnswer}
                    >
                      Проверить ответ <ArrowRight size={17} />
                    </button>
                  )}
                  {lesson.completed && !answerResult && (
                    <div className="checkpoint-result correct">
                      <CheckCircle2 />
                      <strong>Этот урок уже пройден</strong>
                    </div>
                  )}
                </div>
              )}
            </article>
          </div>
        )}
      </div>
    </section>
  );
}

