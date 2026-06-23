"use client";

import {
  AlertTriangle,
  CheckCircle2,
  FileWarning,
  PhoneCall,
  Search,
  ShieldQuestion,
} from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";
import { scamLabels } from "@/lib/scam-data";
import { NumberCheck } from "@/lib/types";

export default function NumbersPage() {
  const { user } = useAuth();
  const [phone, setPhone] = useState("+998");
  const [result, setResult] = useState<NumberCheck | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [reportOpen, setReportOpen] = useState(false);
  const [reportSent, setReportSent] = useState(false);

  const check = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await api<NumberCheck>(
          `/scammer-db/check/?phone=${encodeURIComponent(phone)}`,
        ),
      );
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const sendReport = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError("");
    try {
      await api("/scammer-db/reports/", {
        method: "POST",
        auth: true,
        body: JSON.stringify({
          phone,
          scam_type: form.get("scam_type"),
          incident_date: form.get("incident_date"),
          story: form.get("story"),
          region: form.get("region"),
          damage_amount: form.get("damage_amount") || null,
        }),
      });
      setReportSent(true);
      setReportOpen(false);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const statusTone =
    result?.status === "verified_scammer" || result?.status === "scammer"
      ? "danger"
      : result?.status === "suspicious"
        ? "warning"
        : "neutral";

  return (
    <section className="page-section numbers-page">
      <div className="container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <PhoneCall size={15} /> Общественная база
          </span>
          <h1>Проверьте номер телефона</h1>
          <p>
            Узнайте, есть ли подтверждённые жалобы от других пользователей.
          </p>
          <Link
            className="button button-danger report-primary-cta"
            href="/numbers/report"
          >
            <FileWarning size={17} /> Сообщить о мошенничестве
          </Link>
        </div>

        <form className="phone-search" onSubmit={check}>
          <span className="phone-prefix">UZ</span>
          <input
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="+998 90 123 45 67"
            required
          />
          <button className="button button-primary" disabled={busy}>
            <Search size={18} />
            {busy ? "Проверяем..." : "Проверить"}
          </button>
        </form>

        {error && <div className="form-error centered">{error}</div>}
        {reportSent && (
          <div className="success-banner">
            <CheckCircle2 /> Жалоба отправлена на модерацию. Спасибо, что
            помогаете другим.
          </div>
        )}

        {result && (
          <div className={`number-result ${statusTone}`}>
            <div className="number-result-icon">
              {result.found ? (
                statusTone === "danger" ? (
                  <AlertTriangle />
                ) : (
                  <FileWarning />
                )
              ) : (
                <ShieldQuestion />
              )}
            </div>
            <div className="number-result-main">
              <StatusPill tone={statusTone}>
                {result.status === "not_found"
                  ? "Жалоб не найдено"
                  : result.status === "suspicious"
                    ? "Подозрительный"
                    : result.status === "verified_scammer"
                      ? "Подтверждено ЦКБ"
                      : "Высокий риск"}
              </StatusPill>
              <h2>{result.phone_masked || phone}</h2>
              {result.found ? (
                <>
                  <p>
                    Подтверждённых жалоб:{" "}
                    <strong>{result.approved_reports_count}</strong>
                  </p>
                  <div className="tag-list">
                    {result.scam_types?.map((type) => (
                      <span key={type}>{scamLabels[type] || type}</span>
                    ))}
                  </div>
                </>
              ) : (
                <p>
                  Одобренных жалоб пока нет. Это не доказывает, что номер
                  безопасен.
                </p>
              )}
            </div>
            <Link className="button button-ghost" href="/numbers/report">
              <FileWarning size={17} /> Сообщить о номере
            </Link>
          </div>
        )}

        {result?.reports && result.reports.length > 0 && (
          <div className="story-section">
            <h2>Подтверждённые истории</h2>
            <div className="story-grid">
              {result.reports.map((report, index) => (
                <article className="story-card" key={`${report.story}-${index}`}>
                  <div>
                    <StatusPill tone="warning">
                      {scamLabels[report.scam_type] || report.scam_type}
                    </StatusPill>
                    <small>{report.incident_date}</small>
                  </div>
                  <p>{report.story}</p>
                  <span>{report.region}</span>
                </article>
              ))}
            </div>
          </div>
        )}

        <div className="safety-callout">
          <AlertTriangle />
          <div>
            <strong>Номер не найден — не значит номер безопасен</strong>
            <p>
              База содержит только одобренные модераторами жалобы. Всегда
              проверяйте личность звонящего через официальный канал.
            </p>
          </div>
        </div>

        {reportOpen && (
          <div className="modal-backdrop" onMouseDown={() => setReportOpen(false)}>
            <div className="modal-card" onMouseDown={(event) => event.stopPropagation()}>
              <button className="modal-close" onClick={() => setReportOpen(false)}>
                ×
              </button>
              <span className="eyebrow">Помогите сообществу</span>
              <h2>Сообщить о мошенничестве</h2>
              {!user ? (
                <div className="login-prompt">
                  <p>Чтобы отправить жалобу, войдите по номеру телефона.</p>
                  <Link className="button button-primary" href="/login">
                    Войти
                  </Link>
                </div>
              ) : (
                <form className="form-stack" onSubmit={sendReport}>
                  <label>
                    Тип мошенничества
                    <select name="scam_type" required defaultValue="bank_call">
                      {Object.entries(scamLabels).map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="form-row">
                    <label>
                      Дата
                      <input name="incident_date" type="date" required />
                    </label>
                    <label>
                      Регион
                      <input name="region" placeholder="tashkent" required />
                    </label>
                  </div>
                  <label>
                    Что произошло?
                    <textarea
                      name="story"
                      minLength={20}
                      maxLength={1000}
                      placeholder="Опишите звонок или переписку без личных данных..."
                      required
                    />
                  </label>
                  <label>
                    Сумма ущерба, UZS (необязательно)
                    <input name="damage_amount" type="number" min="0" />
                  </label>
                  <button className="button button-primary button-wide">
                    Отправить на проверку
                  </button>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
