"use client";

import {
  Award,
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
import { api } from "@/lib/api";
import { scamLabels } from "@/lib/scam-data";

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
  const [reports, setReports] = useState<Report[]>([]);

  useEffect(() => {
    if (user) {
      api<Report[]>("/scammer-db/reports/my/", { auth: true })
        .then(setReports)
        .catch(() => setReports([]));
    }
  }, [user]);

  if (loading) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" /> Открываем кабинет...
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
          <h1>Войдите в личный кабинет</h1>
          <p>Здесь хранятся ваши сертификаты, баллы и обращения.</p>
          <Link className="button button-primary" href="/login">
            Войти
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="page-section account-page">
      <div className="container">
        <div className="account-hero">
          <div className="avatar">
            {(user.full_name || "C").slice(0, 1).toUpperCase()}
          </div>
          <div>
            <span className="eyebrow">Личный кабинет</span>
            <h1>{user.full_name || "Пользователь CyberSafe"}</h1>
            <p>{user.phone_masked}</p>
          </div>
          <StatusPill tone="safe">
            <ShieldCheck size={15} /> Номер подтверждён
          </StatusPill>
        </div>

        <div className="dashboard-grid">
          <article className="metric-card">
            <span className="metric-icon blue">
              <Star />
            </span>
            <div>
              <strong>{user.points}</strong>
              <p>Баллов защиты</p>
            </div>
          </article>
          <Link href="/certificates" className="metric-card">
            <span className="metric-icon violet">
              <Award />
            </span>
            <div>
              <strong>Сертификаты</strong>
              <p>Открыть документы</p>
            </div>
            <ChevronRight />
          </Link>
          <Link href="/quiz" className="metric-card">
            <span className="metric-icon green">
              <ShieldCheck />
            </span>
            <div>
              <strong>Новый тест</strong>
              <p>Проверить знания</p>
            </div>
            <ChevronRight />
          </Link>
          <Link href="/courses" className="metric-card">
            <span className="metric-icon cyan">
              <GraduationCap />
            </span>
            <div>
              <strong>Курсы</strong>
              <p>Продолжить обучение</p>
            </div>
            <ChevronRight />
          </Link>
          <Link href="/simulator" className="metric-card">
            <span className="metric-icon red">
              <BrainCircuit />
            </span>
            <div>
              <strong>Симулятор</strong>
              <p>Отразить атаку</p>
            </div>
            <ChevronRight />
          </Link>
        </div>

        <div className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Сообщество</span>
              <h2>Мои жалобы</h2>
            </div>
            <div className="panel-actions">
              <Link href="/numbers" className="text-link">
                Проверить номер <ChevronRight size={17} />
              </Link>
              <Link
                href="/numbers/report"
                className="button button-small button-danger"
              >
                Подать заявку
              </Link>
            </div>
          </div>
          {reports.length === 0 ? (
            <div className="panel-empty">
              <FileWarning />
              <p>Вы ещё не отправляли жалобы на подозрительные номера.</p>
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
                      Заявка #{report.id.slice(0, 8)} ·{" "}
                      {scamLabels[report.scam_type] || report.scam_type}
                    </p>
                    <small>
                      Подана{" "}
                      {new Date(report.created_at).toLocaleDateString("ru-RU")}
                    </small>
                    {report.moderator_comment && (
                      <small className="moderator-comment">
                        Комментарий: {report.moderator_comment}
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
                      ? "Одобрено"
                      : report.status === "rejected"
                        ? "Отклонено"
                        : "На проверке"}
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
