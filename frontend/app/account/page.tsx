"use client";

import {
  Award,
  CalendarCheck,
  ChevronRight,
  FileWarning,
  GraduationCap,
  BrainCircuit,
  LogIn,
  ShieldCheck,
  Star,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { getScamLabel } from "@/lib/scam-data";
import { Certificate, Course, DailyQuizStatus } from "@/lib/types";

type Report = {
  id: string;
  phone_masked: string;
  scam_type: string;
  status: "pending" | "approved" | "rejected";
  moderator_comment: string;
  created_at: string;
};

export default function AccountPage() {
  const { user, loading } = useAuth();
  const { language, t } = useLanguage();
  const [reports, setReports] = useState<Report[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [dailyStatus, setDailyStatus] = useState<DailyQuizStatus | null>(null);

  useEffect(() => {
    if (user) {
      Promise.all([
        api<Report[]>("/scammer-db/reports/my/", { auth: true }).catch(
          () => [],
        ),
        api<Course[]>(`/courses/?language=${language}`, { auth: true }).catch(
          () => [],
        ),
        api<Certificate[]>("/certificates/", { auth: true }).catch(() => []),
        api<DailyQuizStatus>(`/quiz/daily/?language=${language}`, {
          auth: true,
        }).catch(() => null),
      ]).then(([nextReports, nextCourses, nextCertificates, nextDaily]) => {
        setReports(nextReports);
        setCourses(nextCourses);
        setCertificates(nextCertificates);
        setDailyStatus(nextDaily);
      });
    }
  }, [language, user]);

  if (loading) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" /> {t("account.loading")}
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <span className="empty-icon">
            <LogIn />
          </span>
          <h1>{t("account.loginTitle")}</h1>
          <p>{t("account.loginText")}</p>
          <Link className="button button-primary" href="/login">
            {t("common.login")}
          </Link>
        </div>
      </section>
    );
  }

  const totalLessons = courses.reduce(
    (sum, course) => sum + course.lessons_count,
    0,
  );
  const completedLessons = courses.reduce(
    (sum, course) => sum + course.completed_lessons,
    0,
  );
  const courseProgress = totalLessons
    ? Math.round((completedLessons * 100) / totalLessons)
    : 0;
  const pendingReports = reports.filter((report) => report.status === "pending")
    .length;

  return (
    <section className="page-section account-page">
      <div className="container">
        <div className="account-hero">
          <div className="avatar">
            {(user.full_name || "C").slice(0, 1).toUpperCase()}
          </div>
          <div>
            <span className="eyebrow">{t("account.eyebrow")}</span>
            <h1>{user.full_name || t("account.user")}</h1>
            <p>{user.phone_masked}</p>
          </div>
          <StatusPill tone="safe">
            <ShieldCheck size={15} /> {t("account.verified")}
          </StatusPill>
        </div>

        <div className="dashboard-grid">
          <article className="metric-card">
            <span className="metric-icon blue">
              <Star />
            </span>
            <div>
              <strong>{user.points}</strong>
              <p>{t("account.points")}</p>
            </div>
          </article>
          <Link href="/certificates" className="metric-card">
            <span className="metric-icon violet">
              <Award />
            </span>
            <div>
              <strong>{certificates.length}</strong>
              <p>{t("account.certificates")}</p>
            </div>
            <ChevronRight />
          </Link>
          <Link href="/quiz" className="metric-card">
            <span className="metric-icon green">
              <ShieldCheck />
            </span>
            <div>
              <strong>{t("account.newQuiz")}</strong>
              <p>{t("account.checkKnowledge")}</p>
            </div>
            <ChevronRight />
          </Link>
          <Link href="/courses" className="metric-card">
            <span className="metric-icon cyan">
              <GraduationCap />
            </span>
            <div>
              <strong>{courseProgress}%</strong>
              <p>
                {completedLessons}/{totalLessons} {t("account.courses")}
              </p>
            </div>
            <ChevronRight />
          </Link>
          <Link href="/daily-quiz" className="metric-card">
            <span className="metric-icon green">
              <CalendarCheck />
            </span>
            <div>
              <strong>{dailyStatus?.streak || 0}</strong>
              <p>
                {language === "uz" ? "Kunlik seriya" : "Дней серии"} ·{" "}
                {dailyStatus?.completed
                  ? language === "uz"
                    ? "bugun bajarildi"
                    : "сегодня пройден"
                  : language === "uz"
                    ? "bugun ochiq"
                    : "сегодня доступен"}
              </p>
            </div>
            <ChevronRight />
          </Link>
          <Link href="/simulator" className="metric-card">
            <span className="metric-icon red">
              <BrainCircuit />
            </span>
            <div>
              <strong>{t("account.simulator")}</strong>
              <p>{t("account.repulseAttack")}</p>
            </div>
            <ChevronRight />
          </Link>
          <article className="metric-card">
            <span className="metric-icon red">
              <FileWarning />
            </span>
            <div>
              <strong>{pendingReports}</strong>
              <p>
                {language === "uz"
                  ? "Kutilayotgan arizalar"
                  : "Заявок на проверке"}
              </p>
            </div>
          </article>
        </div>

        <div className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">{t("account.community")}</span>
              <h2>{t("account.reports")}</h2>
            </div>
            <div className="panel-actions">
              <Link href="/analyzer#phone" className="text-link">
                {t("account.checkNumber")} <ChevronRight size={17} />
              </Link>
              <Link
                href="/numbers/report"
                className="button button-small button-danger"
              >
                {t("account.submitReport")}
              </Link>
            </div>
          </div>
          {reports.length === 0 ? (
            <div className="panel-empty">
              <FileWarning />
              <p>{t("account.noReports")}</p>
            </div>
          ) : (
            <div className="report-list">
              {reports.map((report) => (
                <div className="report-row" key={report.id}>
                  <span className="report-icon">
                    <FileWarning />
                  </span>
                  <div>
                    <strong>{report.phone_masked}</strong>
                    <p>
                      {t("account.report", { id: report.id.slice(0, 8) })} ·{" "}
                      {getScamLabel(report.scam_type, language)}
                    </p>
                    <small>
                      {t("account.submitted")}{" "}
                      {new Date(report.created_at).toLocaleDateString(
                        language === "uz" ? "uz-UZ" : "ru-RU",
                      )}
                    </small>
                    {report.moderator_comment && (
                      <small className="moderator-comment">
                        {t("account.comment")} {report.moderator_comment}
                      </small>
                    )}
                  </div>
                  <StatusPill
                    tone={
                      report.status === "approved"
                        ? "safe"
                        : report.status === "rejected"
                          ? "danger"
                          : "warning"
                    }
                  >
                    {report.status === "approved"
                      ? t("status.approved")
                      : report.status === "rejected"
                        ? t("status.rejected")
                        : t("status.pending")}
                  </StatusPill>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
