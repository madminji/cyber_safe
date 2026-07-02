"use client";

import {
  ArrowLeft,
  BookOpenCheck,
  Check,
  Clock3,
  LockKeyhole,
  PlayCircle,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { CourseDetail } from "@/lib/types";

export default function CourseDetailPage() {
  const params = useParams<{ id: string }>();
  const { user, loading } = useAuth();
  const { language, t } = useLanguage();
  const [course, setCourse] = useState<CourseDetail | null>(null);
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

  if (busy && !course) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" /> {t("course.loading")}
        </div>
      </section>
    );
  }

  if (!course) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <h1>{t("course.notFound")}</h1>
          <p>{error}</p>
          <Link href="/courses" className="button button-primary">
            {t("course.back")}
          </Link>
        </div>
      </section>
    );
  }

  const levelLabel = {
    basic: t("common.basic"),
    advanced: t("common.advanced"),
    expert: t("common.expert"),
  }[course.level];

  return (
    <section className="page-section course-detail-page">
      <div className="container">
        <Link href="/courses" className="back-link">
          <ArrowLeft size={17} /> {t("course.all")}
        </Link>
        <div className="course-detail-hero">
          <div>
            <span className="eyebrow">{levelLabel}</span>
            <h1>{course.title}</h1>
            <p>{course.description}</p>
            <div className="course-detail-meta">
              <span>
                <BookOpenCheck size={17} /> {course.lessons_count}{" "}
                {t("courses.lessons")}
              </span>
              <span>
                <Clock3 size={17} /> {course.duration_minutes}{" "}
                {t("courses.minutes")}
              </span>
            </div>
          </div>
          <div className="course-progress-orb">
            <strong>{course.progress_percent}%</strong>
            <span>{t("course.completed")}</span>
          </div>
        </div>

        <div className="lesson-list">
          {course.lessons.map((item) => (
            <Link
              className={item.completed ? "lesson-row completed" : "lesson-row"}
              key={item.id}
              href={
                user
                  ? `/courses/${course.id}/lessons/${item.id}`
                  : `/login?next=/courses/${course.id}/lessons/${item.id}`
              }
            >
              <span className="lesson-order">
                {item.completed ? <Check size={18} /> : item.order}
              </span>
              <div>
                <strong>{item.title}</strong>
                <p>{item.summary}</p>
              </div>
              <span className="lesson-duration">
                <Clock3 size={14} /> {item.duration_minutes}{" "}
                {t("course.minuteShort")}
              </span>
              {user ? <PlayCircle /> : <LockKeyhole />}
            </Link>
          ))}
        </div>

        {!user && (
          <div className="course-login-callout">
            <LockKeyhole />
            <div>
              <strong>{t("course.loginTitle")}</strong>
              <p>{t("course.loginText")}</p>
            </div>
            <Link href="/login" className="button button-primary button-small">
              {t("common.login")}
            </Link>
          </div>
        )}

      </div>
    </section>
  );
}
