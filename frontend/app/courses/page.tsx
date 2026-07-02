"use client";

import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Clock3,
  GraduationCap,
  Layers3,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { Course } from "@/lib/types";

export default function CoursesPage() {
  const { user, loading } = useAuth();
  const { language, t } = useLanguage();
  const [courses, setCourses] = useState<Course[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (loading) return;
    setBusy(true);
    api<Course[]>(`/courses/?language=${language}`, { auth: Boolean(user) })
      .then(setCourses)
      .catch((requestError) => setError(requestError.message))
      .finally(() => setBusy(false));
  }, [language, loading, user]);

  const levelLabels = {
    basic: t("common.basic"),
    advanced: t("common.advanced"),
    expert: t("common.expert"),
  };
  const orderedCourses = [...courses].sort(
    (first, second) =>
      ["basic", "advanced", "expert"].indexOf(first.level) -
      ["basic", "advanced", "expert"].indexOf(second.level),
  );
  const levelDescriptions = {
    basic: t("courses.pathBasic"),
    advanced: t("courses.pathAdvanced"),
    expert: t("courses.pathExpert"),
  };

  return (
    <section className="page-section courses-page">
      <div className="container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <GraduationCap size={16} /> {t("courses.eyebrow")}
          </span>
          <h1>{t("courses.title")}</h1>
          <p>{t("courses.lead")}</p>
        </div>

        {busy ? (
          <div className="loading-card">
            <span className="loader" /> {t("courses.loading")}
          </div>
        ) : error ? (
          <div className="form-error centered">{error}</div>
        ) : (
          <>
            <div className="course-path">
              {orderedCourses.map((course, index) => (
                <Link
                  href={`/courses/${course.id}`}
                  className={`course-path-step ${course.level}`}
                  key={course.id}
                >
                  <span className="path-number">{index + 1}</span>
                  <div>
                    <small>{levelLabels[course.level]}</small>
                    <strong>{course.title.replace("CyberSafe ", "")}</strong>
                    <p>{levelDescriptions[course.level]}</p>
                    {user && (
                      <div className="progress-track compact-progress">
                        <span style={{ width: `${course.progress_percent}%` }} />
                      </div>
                    )}
                  </div>
                  <ArrowRight size={18} />
                </Link>
              ))}
            </div>

            <div className="courses-grid">
              {orderedCourses.map((course, index) => (
              <article className="course-card" key={course.id}>
                <div className={`course-cover course-cover-${(index % 3) + 1}`}>
                  <span className="course-level">
                    {levelLabels[course.level]}
                  </span>
                  <BookOpen size={58} strokeWidth={1.25} />
                  <span className="course-index">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
                <div className="course-body">
                  <div className="course-meta">
                    <span>
                      <Layers3 size={14} /> {course.lessons_count}{" "}
                      {t("courses.lessons")}
                    </span>
                    <span>
                      <Clock3 size={14} /> {course.duration_minutes}{" "}
                      {t("courses.minutes")}
                    </span>
                  </div>
                  <h2>{course.title}</h2>
                  <p>{course.description}</p>
                  {user && (
                    <div className="course-progress">
                      <div>
                        <span>{t("courses.progress")}</span>
                        <strong>{course.progress_percent}%</strong>
                      </div>
                      <div className="progress-track compact-progress">
                        <span style={{ width: `${course.progress_percent}%` }} />
                      </div>
                      <small>
                        <CheckCircle2 size={13} />
                        {course.completed_lessons} {t("courses.of")}{" "}
                        {course.lessons_count}
                      </small>
                    </div>
                  )}
                  <Link
                    className="button button-primary button-wide"
                    href={`/courses/${course.id}`}
                  >
                    {course.progress_percent > 0
                      ? t("courses.continue")
                      : t("courses.open")}
                    <ArrowRight size={17} />
                  </Link>
                </div>
                </article>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
}
