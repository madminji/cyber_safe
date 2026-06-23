"use client";

import {
  AlertTriangle,
  BadgeCheck,
  Check,
  CheckCircle2,
  Clock3,
  FileSearch,
  Gavel,
  ListFilter,
  RefreshCw,
  ShieldAlert,
  UserRound,
  X,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";
import { regions, scamLabels } from "@/lib/scam-data";
import { ModerationReport, ModerationSummary } from "@/lib/types";

type Filter = "pending" | "approved" | "rejected";

const regionLabels = Object.fromEntries(
  regions.map((region) => [region.value, region.label]),
) as Record<string, string>;

export default function ModerationPage() {
  const { user, loading } = useAuth();
  const [filter, setFilter] = useState<Filter>("pending");
  const [reports, setReports] = useState<ModerationReport[]>([]);
  const [summary, setSummary] = useState<ModerationSummary | null>(null);
  const [selected, setSelected] = useState<ModerationReport | null>(null);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const canModerate =
    user?.role === "moderator" || user?.role === "admin";

  const loadData = useCallback(async () => {
    if (!canModerate) return;
    setBusy(true);
    setError("");
    try {
      const [queue, counters] = await Promise.all([
        api<ModerationReport[]>(
          `/scammer-db/moderation/reports/?status=${filter}`,
          { auth: true },
        ),
        api<ModerationSummary>("/scammer-db/moderation/summary/", {
          auth: true,
        }),
      ]);
      setReports(queue);
      setSummary(counters);
      if (selected) {
        const updated = queue.find((item) => item.id === selected.id);
        setSelected(updated || null);
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  }, [canModerate, filter, selected]);

  useEffect(() => {
    if (!loading) loadData();
    // Selected report is intentionally excluded to avoid a reload loop.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, filter, canModerate]);

  const moderate = async (status: "approved" | "rejected") => {
    if (!selected) return;
    if (status === "rejected" && comment.trim().length < 5) {
      setError("При отклонении укажите причину минимум из 5 символов.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api(
        `/scammer-db/moderation/reports/${selected.id}/`,
        {
          method: "PATCH",
          auth: true,
          body: JSON.stringify({
            status,
            moderator_comment: comment.trim(),
          }),
        },
      );
      setSelected(null);
      setComment("");
      await loadData();
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const toggleVerification = async () => {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      await api(
        `/scammer-db/moderation/numbers/${selected.number_id}/verification/`,
        {
          method: "PATCH",
          auth: true,
          body: JSON.stringify({ verified: !selected.number_verified }),
        },
      );
      setSelected({
        ...selected,
        number_verified: !selected.number_verified,
        number_status: selected.number_verified
          ? selected.approved_reports_count >= 4
            ? "scammer"
            : selected.approved_reports_count >= 1
              ? "suspicious"
              : "reported"
          : "verified_scammer",
      });
      await loadData();
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
          <span className="loader" /> Проверяем права доступа...
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <Gavel />
          <h1>Требуется авторизация</h1>
          <Link className="button button-primary" href="/login?next=/moderation">
            Войти
          </Link>
        </div>
      </section>
    );
  }

  if (!canModerate) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <ShieldAlert />
          <h1>Доступ запрещён</h1>
          <p>Эта страница доступна только модераторам и администраторам.</p>
          <Link className="button button-primary" href="/">
            На главную
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="page-section moderation-page">
      <div className="container">
        <div className="moderation-heading">
          <div>
            <span className="eyebrow">
              <Gavel size={16} /> Внутренняя панель
            </span>
            <h1>Модерация заявок</h1>
            <p>
              Проверяйте обращения граждан до публикации номера в общей базе.
            </p>
          </div>
          <button
            className="button button-ghost"
            onClick={loadData}
            disabled={busy}
          >
            <RefreshCw size={17} /> Обновить
          </button>
        </div>

        {summary && (
          <div className="moderation-metrics">
            <article className="pending">
              <Clock3 />
              <div>
                <strong>{summary.pending}</strong>
                <span>Ожидают решения</span>
              </div>
            </article>
            <article className="approved">
              <CheckCircle2 />
              <div>
                <strong>{summary.approved}</strong>
                <span>Одобрено</span>
              </div>
            </article>
            <article className="rejected">
              <XCircle />
              <div>
                <strong>{summary.rejected}</strong>
                <span>Отклонено</span>
              </div>
            </article>
            <article className="verified">
              <BadgeCheck />
              <div>
                <strong>{summary.verified_numbers}</strong>
                <span>Верифицировано ЦКБ</span>
              </div>
            </article>
          </div>
        )}

        <div className="moderation-toolbar">
          <div className="moderation-filters">
            <ListFilter size={17} />
            {(["pending", "approved", "rejected"] as Filter[]).map(
              (status) => (
                <button
                  key={status}
                  className={filter === status ? "active" : ""}
                  onClick={() => {
                    setFilter(status);
                    setSelected(null);
                  }}
                >
                  {status === "pending"
                    ? "На модерации"
                    : status === "approved"
                      ? "Одобренные"
                      : "Отклонённые"}
                </button>
              ),
            )}
          </div>
          {summary && (
            <span className="reports-today">
              Сегодня поступило: <strong>{summary.reports_today}</strong>
            </span>
          )}
        </div>

        {error && <div className="form-error centered">{error}</div>}

        <div className="moderation-layout">
          <div className="moderation-list">
            {busy && reports.length === 0 ? (
              <div className="loading-card">
                <span className="loader" /> Загружаем очередь...
              </div>
            ) : reports.length === 0 ? (
              <div className="panel-empty moderation-empty">
                <FileSearch />
                <p>В этом разделе заявок нет.</p>
              </div>
            ) : (
              reports.map((report) => (
                <button
                  key={report.id}
                  className={
                    selected?.id === report.id
                      ? "moderation-list-item active"
                      : "moderation-list-item"
                  }
                  onClick={() => {
                    setSelected(report);
                    setComment(report.moderator_comment || "");
                    setError("");
                  }}
                >
                  <span className="moderation-item-icon">
                    <AlertTriangle />
                  </span>
                  <div>
                    <strong>{report.phone_masked}</strong>
                    <p>{scamLabels[report.scam_type] || report.scam_type}</p>
                    <small>
                      #{report.id.slice(0, 8)} ·{" "}
                      {new Date(report.created_at).toLocaleDateString("ru-RU")}
                    </small>
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
                        : "Ожидает"}
                  </StatusPill>
                </button>
              ))
            )}
          </div>

          <aside className="moderation-detail">
            {!selected ? (
              <div className="moderation-placeholder">
                <FileSearch />
                <h2>Выберите заявку</h2>
                <p>Здесь появятся детали и действия модератора.</p>
              </div>
            ) : (
              <>
                <div className="moderation-detail-head">
                  <div>
                    <span className="eyebrow">
                      Заявка #{selected.id.slice(0, 8)}
                    </span>
                    <h2>{selected.phone_masked}</h2>
                  </div>
                  <button
                    className="detail-close"
                    onClick={() => setSelected(null)}
                    aria-label="Закрыть заявку"
                  >
                    <X />
                  </button>
                </div>

                <div className="number-state">
                  <div>
                    <span>Статус номера</span>
                    <strong>
                      {selected.number_status === "verified_scammer"
                        ? "Верифицированный мошенник"
                        : selected.number_status === "scammer"
                          ? "Мошенник"
                          : selected.number_status === "suspicious"
                            ? "Подозрительный"
                            : "Новый"}
                    </strong>
                  </div>
                  <div>
                    <span>Одобренных жалоб</span>
                    <strong>{selected.approved_reports_count}</strong>
                  </div>
                </div>

                <dl className="report-facts">
                  <div>
                    <dt>Вид мошенничества</dt>
                    <dd>
                      {scamLabels[selected.scam_type] || selected.scam_type}
                    </dd>
                  </div>
                  <div>
                    <dt>Дата происшествия</dt>
                    <dd>
                      {new Date(selected.incident_date).toLocaleDateString(
                        "ru-RU",
                      )}
                    </dd>
                  </div>
                  <div>
                    <dt>Регион</dt>
                    <dd>
                      {regionLabels[selected.region] || selected.region}
                    </dd>
                  </div>
                  <div>
                    <dt>Ущерб</dt>
                    <dd>
                      {selected.damage_amount
                        ? `${Number(selected.damage_amount).toLocaleString(
                            "ru-RU",
                          )} UZS`
                        : "Не указан"}
                    </dd>
                  </div>
                  <div>
                    <dt>Заявитель</dt>
                    <dd>{selected.reporter_name || "Без имени"}</dd>
                  </div>
                </dl>

                <div className="report-story">
                  <strong>Описание гражданина</strong>
                  <p>{selected.story}</p>
                </div>

                <label className="moderator-comment-field">
                  Комментарий модератора
                  <textarea
                    value={comment}
                    onChange={(event) => setComment(event.target.value)}
                    maxLength={500}
                    placeholder="Причина решения или внутреннее примечание..."
                  />
                </label>

                {selected.status === "pending" ? (
                  <div className="moderation-actions">
                    <button
                      className="button moderation-reject"
                      disabled={busy}
                      onClick={() => moderate("rejected")}
                    >
                      <XCircle size={17} /> Отклонить
                    </button>
                    <button
                      className="button moderation-approve"
                      disabled={busy}
                      onClick={() => moderate("approved")}
                    >
                      <Check size={17} /> Одобрить
                    </button>
                  </div>
                ) : (
                  <div className="decision-banner">
                    Решение:{" "}
                    <strong>
                      {selected.status === "approved"
                        ? "заявка одобрена"
                        : "заявка отклонена"}
                    </strong>
                  </div>
                )}

                <button
                  className={
                    selected.number_verified
                      ? "button button-ghost button-wide"
                      : "button button-danger button-wide"
                  }
                  disabled={busy}
                  onClick={toggleVerification}
                >
                  <BadgeCheck size={17} />
                  {selected.number_verified
                    ? "Снять верификацию ЦКБ"
                    : "Подтвердить номер как мошеннический"}
                </button>
              </>
            )}
          </aside>
        </div>
      </div>
    </section>
  );
}

