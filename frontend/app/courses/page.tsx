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

const levelLabels = {
  basic: "Базовый",
  advanced: "Продвинутый",
  expert: "Эксперт",
};

export default function CoursesPage() {
  const { user, loading } = useAuth();
  const { language } = useLanguage();
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

  return (
    <section className="page-section courses-page">
      <div className="container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <GraduationCap size={16} /> Учитесь в своём темпе
          </span>
          <h1>Курсы цифровой безопасности</h1>
          <p>
            Короткие практические уроки, контрольные вопросы и сохранение
            прогресса в личном кабинете.
          </p>
        </div>

        {busy ? (
          <div className="loading-card">
            <span className="loader" /> Загружаем курсы...
          </div>
        ) : error ? (
          <div className="form-error centered">{error}</div>
        ) : (
          <div className="courses-grid">
            {courses.map((course, index) => (
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
                      <Layers3 size={14} /> {course.lessons_count} урока
                    </span>
                    <span>
                      <Clock3 size={14} /> {course.duration_minutes} минут
                    </span>
                  </div>
                  <h2>{course.title}</h2>
                  <p>{course.description}</p>
                  {user && (
                    <div className="course-progress">
                      <div>
                        <span>Прогресс</span>
                        <strong>{course.progress_percent}%</strong>
                      </div>
                      <div className="progress-track compact-progress">
                        <span style={{ width: `${course.progress_percent}%` }} />
                      </div>
                      <small>
                        <CheckCircle2 size={13} />
                        {course.completed_lessons} из {course.lessons_count}
                      </small>
                    </div>
                  )}
                  <Link
                    className="button button-primary button-wide"
                    href={`/courses/${course.id}`}
                  >
                    {course.progress_percent > 0 ? "Продолжить" : "Открыть курс"}
                    <ArrowRight size={17} />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

