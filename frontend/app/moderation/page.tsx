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
  UploadCloud,
  BookOpenText,
  RefreshCw,
  ShieldAlert,
  Download,
  Trash2,
  ExternalLink,
  X,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { getRegions, getScamLabel } from "@/lib/scam-data";
import {
  AdminCourseContent,
  AdminLesson,
  ModerationNumber,
  ModerationReport,
  ModerationSummary,
} from "@/lib/types";

type Filter = "pending" | "approved" | "rejected";
type NumberFilter = "suspicious" | "scammer" | "verified_scammer" | "reported";
type ModerationTab = "reports" | "lessons";
type ReportPanel = "reports" | "numbers";

type LessonImportResult = {
  status: "created" | "updated";
  lesson_id: string;
  lesson_slug: string;
  course_id: string;
  blocks_count: number;
  tasks_count: number;
  questions_count: number;
};

export default function ModerationPage() {
  const { user, loading } = useAuth();
  const { language, t } = useLanguage();
  const [activeTab, setActiveTab] = useState<ModerationTab>("reports");
  const [reportPanel, setReportPanel] = useState<ReportPanel>("reports");
  const [filter, setFilter] = useState<Filter>("pending");
  const [numberFilter, setNumberFilter] = useState<NumberFilter>("suspicious");
  const [reports, setReports] = useState<ModerationReport[]>([]);
  const [numbers, setNumbers] = useState<ModerationNumber[]>([]);
  const [summary, setSummary] = useState<ModerationSummary | null>(null);
  const [selected, setSelected] = useState<ModerationReport | null>(null);
  const [selectedNumber, setSelectedNumber] = useState<ModerationNumber | null>(
    null,
  );
  const [comment, setComment] = useState("");
  const [lessonFile, setLessonFile] = useState<File | null>(null);
  const [lessonImportResult, setLessonImportResult] =
    useState<LessonImportResult | null>(null);
  const [lessonImportError, setLessonImportError] = useState("");
  const [lessonImportBusy, setLessonImportBusy] = useState(false);
  const [courseContent, setCourseContent] = useState<AdminCourseContent[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [contentBusy, setContentBusy] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const canModerate =
    user?.role === "moderator" || user?.role === "admin";
  const canManageLessons = canModerate;
  const regionLabels = Object.fromEntries(
    getRegions(language).map((region) => [region.value, region.label]),
  ) as Record<string, string>;
  const getNumberStatusLabel = (status: ModerationNumber["status"]) =>
    status === "verified_scammer"
      ? t("moderation.verifiedScammer")
      : status === "scammer"
        ? t("moderation.scammer")
        : status === "suspicious"
          ? t("moderation.suspicious")
          : t("moderation.new");
  const getCalculatedNumberStatus = (
    approvedReports: number,
  ): ModerationNumber["status"] =>
    approvedReports >= 4
      ? "scammer"
      : approvedReports >= 1
        ? "suspicious"
        : "reported";

  const loadData = useCallback(async () => {
    if (!canModerate) return;
    setBusy(true);
    setError("");
    try {
      const [queue, numberRegistry, counters] = await Promise.all([
        api<ModerationReport[]>(
          `/scammer-db/moderation/reports/?status=${filter}`,
          { auth: true },
        ),
        api<ModerationNumber[]>(
          `/scammer-db/moderation/numbers/?status=${numberFilter}`,
          { auth: true },
        ),
        api<ModerationSummary>("/scammer-db/moderation/summary/", {
          auth: true,
        }),
      ]);
      setReports(queue);
      setNumbers(numberRegistry);
      setSummary(counters);
      if (selected) {
        const updated = queue.find((item) => item.id === selected.id);
        setSelected(updated || null);
      }
      if (selectedNumber) {
        const updatedNumber = numberRegistry.find(
          (item) => item.number_id === selectedNumber.number_id,
        );
        setSelectedNumber(updatedNumber || null);
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  }, [canModerate, filter, numberFilter, selected, selectedNumber]);

  useEffect(() => {
    if (!loading) loadData();
    // Selected report is intentionally excluded to avoid a reload loop.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, filter, numberFilter, canModerate]);

  const loadCourseContent = useCallback(async () => {
    if (!canManageLessons) return;
    setContentBusy(true);
    setLessonImportError("");
    try {
      const content = await api<AdminCourseContent[]>("/courses/admin/content/", {
        auth: true,
      });
      setCourseContent(content);
      setSelectedCourseId((current) => current || content[0]?.id || "");
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    } finally {
      setContentBusy(false);
    }
  }, [canManageLessons]);

  useEffect(() => {
    if (!loading && activeTab === "lessons") loadCourseContent();
  }, [activeTab, loadCourseContent, loading]);

  const moderate = async (status: "approved" | "rejected") => {
    if (!selected) return;
    if (status === "rejected" && comment.trim().length < 5) {
      setError(t("moderation.rejectReason"));
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
    const target = selectedNumber
      ? {
          id: selectedNumber.number_id,
          verified: selectedNumber.number_verified,
          approvedReports: selectedNumber.approved_reports_count,
        }
      : selected
        ? {
            id: selected.number_id,
            verified: selected.number_verified,
            approvedReports: selected.approved_reports_count,
          }
        : null;
    if (!target) return;
    setBusy(true);
    setError("");
    try {
      const updated = await api<{
        number_id: string;
        phone_masked: string;
        status: ModerationNumber["status"];
        verified_at: string | null;
      }>(`/scammer-db/moderation/numbers/${target.id}/verification/`, {
        method: "PATCH",
        auth: true,
        body: JSON.stringify({ verified: !target.verified }),
      });
      if (selected?.number_id === target.id) {
        setSelected({
          ...selected,
          number_verified: !target.verified,
          number_status: updated.status,
        });
      }
      if (selectedNumber?.number_id === target.id) {
        setSelectedNumber({
          ...selectedNumber,
          number_verified: !target.verified,
          status: updated.status,
          verified_at: updated.verified_at,
        });
      }
      setNumbers((current) =>
        current.map((item) =>
          item.number_id === target.id
            ? {
                ...item,
                number_verified: !target.verified,
                status: updated.status,
                verified_at: updated.verified_at,
              }
            : item,
        ),
      );
      setReports((current) =>
        current.map((item) =>
          item.number_id === target.id
            ? {
                ...item,
                number_verified: !target.verified,
                number_status: target.verified
                  ? getCalculatedNumberStatus(target.approvedReports)
                  : "verified_scammer",
              }
            : item,
        ),
      );
      await loadData();
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const importLessonJson = async () => {
    if (!lessonFile) {
      setLessonImportError("Выберите JSON-файл урока.");
      return;
    }
    setLessonImportBusy(true);
    setLessonImportError("");
    setLessonImportResult(null);
    try {
      const formData = new FormData();
      formData.append("file", lessonFile);
      const result = await api<LessonImportResult>(
        "/courses/admin/lessons/import/",
        {
          method: "POST",
          auth: true,
          body: formData,
        },
      );
      setLessonImportResult(result);
      setLessonFile(null);
      await loadCourseContent();
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    } finally {
      setLessonImportBusy(false);
    }
  };

  const downloadLessonJson = async (lesson: AdminLesson) => {
    try {
      const payload = await api<unknown>(
        `/courses/admin/lessons/${lesson.id}/export/`,
        { auth: true },
      );
      const blob = new Blob([JSON.stringify(payload, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${String(lesson.order).padStart(2, "0")}-${lesson.slug || lesson.id}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    }
  };

  const deleteLesson = async (lesson: AdminLesson) => {
    const confirmed = window.confirm(
      `Удалить урок "${lesson.title}"? Это действие нельзя отменить.`,
    );
    if (!confirmed) return;
    setContentBusy(true);
    setLessonImportError("");
    try {
      await api(`/courses/admin/lessons/${lesson.id}/`, {
        method: "DELETE",
        auth: true,
      });
      await loadCourseContent();
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    } finally {
      setContentBusy(false);
    }
  };

  if (loading) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" /> {t("moderation.checkingAccess")}
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <Gavel />
          <h1>{t("moderation.authRequired")}</h1>
          <Link className="button button-primary" href="/login?next=/moderation">
            {t("common.login")}
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
          <h1>{t("moderation.accessDenied")}</h1>
          <p>{t("moderation.accessText")}</p>
          <Link className="button button-primary" href="/">
            {t("moderation.home")}
          </Link>
        </div>
      </section>
    );
  }

  const selectedCourse =
    courseContent.find((course) => course.id === selectedCourseId) ||
    courseContent[0] ||
    null;

  return (
    <section className="page-section moderation-page">
      <div className="container">
        <div className="moderation-heading">
          <div>
            <span className="eyebrow">
              <Gavel size={16} /> {t("moderation.eyebrow")}
            </span>
            <h1>{t("moderation.title")}</h1>
            <p>{t("moderation.lead")}</p>
          </div>
          <button
            className="button button-ghost"
            onClick={loadData}
            disabled={busy}
          >
            <RefreshCw size={17} /> {t("moderation.refresh")}
          </button>
        </div>

        <div className="moderation-section-tabs">
          <button
            className={activeTab === "reports" ? "active" : ""}
            onClick={() => setActiveTab("reports")}
          >
            <Gavel size={17} /> Заявки
          </button>
          <button
            className={activeTab === "lessons" ? "active" : ""}
            onClick={() => setActiveTab("lessons")}
          >
            <BookOpenText size={17} /> Уроки
          </button>
        </div>

        {activeTab === "reports" && summary && (
          <div className="moderation-metrics">
            <article className="pending">
              <Clock3 />
              <div>
                <strong>{summary.pending}</strong>
                <span>{t("moderation.waiting")}</span>
              </div>
            </article>
            <article className="approved">
              <CheckCircle2 />
              <div>
                <strong>{summary.approved}</strong>
                <span>{t("status.approved")}</span>
              </div>
            </article>
            <article className="rejected">
              <XCircle />
              <div>
                <strong>{summary.rejected}</strong>
                <span>{t("status.rejected")}</span>
              </div>
            </article>
            <article className="verified">
              <BadgeCheck />
              <div>
                <strong>{summary.verified_numbers}</strong>
                <span>{t("moderation.verified")}</span>
              </div>
            </article>
          </div>
        )}

        {activeTab === "reports" && (
        <div className="moderation-toolbar">
          <div className="moderation-filters">
            <ListFilter size={17} />
            {(["reports", "numbers"] as ReportPanel[]).map((panel) => (
              <button
                key={panel}
                className={reportPanel === panel ? "active" : ""}
                onClick={() => {
                  setReportPanel(panel);
                  setSelected(null);
                  setSelectedNumber(null);
                }}
              >
                {panel === "reports" ? "Заявки граждан" : "Реестр номеров"}
              </button>
            ))}
            <span className="moderation-filter-divider" />
            {reportPanel === "reports"
              ? (["pending", "approved", "rejected"] as Filter[]).map((status) => (
                <button
                  key={status}
                  className={filter === status ? "active" : ""}
                  onClick={() => {
                    setFilter(status);
                    setSelected(null);
                  }}
                >
                  {status === "pending"
                    ? t("moderation.pendingTab")
                    : status === "approved"
                      ? t("moderation.approvedTab")
                      : t("moderation.rejectedTab")}
                </button>
                ))
              : (
                [
                  "suspicious",
                  "scammer",
                  "verified_scammer",
                  "reported",
                ] as NumberFilter[]
              ).map((status) => (
                <button
                  key={status}
                  className={numberFilter === status ? "active" : ""}
                  onClick={() => {
                    setNumberFilter(status);
                    setSelectedNumber(null);
                  }}
                >
                  {getNumberStatusLabel(status)}
                </button>
              ))}
          </div>
          {summary && (
            <span className="reports-today">
              {t("moderation.today")} <strong>{summary.reports_today}</strong>
            </span>
          )}
        </div>
        )}

        {error && <div className="form-error centered">{error}</div>}

        {activeTab === "lessons" && canManageLessons && (
          <section className="moderation-admin-panel">
            <div className="admin-panel-head">
              <span>
                <BookOpenText size={18} /> Управление контентом
              </span>
              <strong>Импорт JSON-урока</strong>
              <p>
                Загрузите один JSON-файл урока в унифицированном формате.
                Повторная загрузка обновит урок без дублей.
              </p>
            </div>
            <div className="lesson-import-box">
              <label>
                JSON-файл урока
                <input
                  accept="application/json,.json"
                  type="file"
                  onChange={(event) => {
                    setLessonFile(event.target.files?.[0] || null);
                    setLessonImportError("");
                    setLessonImportResult(null);
                  }}
                />
              </label>
              <button
                className="button button-primary"
                disabled={!lessonFile || lessonImportBusy}
                onClick={importLessonJson}
              >
                <UploadCloud size={17} />
                {lessonImportBusy ? "Загружаем..." : "Импортировать урок"}
              </button>
            </div>
            {lessonFile && (
              <div className="admin-file-note">
                Выбран файл: <strong>{lessonFile.name}</strong>
              </div>
            )}
            {lessonImportError && (
              <div className="form-error">{lessonImportError}</div>
            )}
            {lessonImportResult && (
              <div className="admin-import-result">
                <CheckCircle2 size={18} />
                <div>
                  <strong>
                    Урок{" "}
                    {lessonImportResult.status === "created"
                      ? "создан"
                      : "обновлён"}
                  </strong>
                  <p>
                    slug: {lessonImportResult.lesson_slug} · блоков:{" "}
                    {lessonImportResult.blocks_count} · заданий:{" "}
                    {lessonImportResult.tasks_count} · вопросов:{" "}
                    {lessonImportResult.questions_count}
                  </p>
                </div>
              </div>
            )}
            <div className="content-manager">
              <div className="content-manager-head">
                <div>
                  <strong>Курсы и уроки</strong>
                  <p>Просмотр, скачивание JSON и удаление уроков.</p>
                </div>
                <button
                  className="button button-ghost button-small"
                  disabled={contentBusy}
                  onClick={loadCourseContent}
                >
                  <RefreshCw size={15} /> Обновить
                </button>
              </div>

              {contentBusy && courseContent.length === 0 ? (
                <div className="loading-card">
                  <span className="loader" /> Загружаем курсы...
                </div>
              ) : courseContent.length === 0 ? (
                <div className="panel-empty moderation-empty">
                  <BookOpenText />
                  <p>Курсы пока не найдены.</p>
                </div>
              ) : (
                <div className="content-manager-grid">
                  <aside className="content-course-list">
                    {courseContent.map((course) => (
                      <button
                        className={selectedCourse?.id === course.id ? "active" : ""}
                        key={course.id}
                        onClick={() => setSelectedCourseId(course.id)}
                      >
                        <strong>{course.title}</strong>
                        <span>
                          {course.level} · {course.lessons_count} уроков ·{" "}
                          {course.is_published ? "опубликован" : "скрыт"}
                        </span>
                      </button>
                    ))}
                  </aside>

                  <div className="content-lesson-list">
                    {selectedCourse?.lessons.map((lesson) => (
                      <article key={lesson.id}>
                        <div>
                          <span>
                            #{lesson.order} · {lesson.module_title || "Без модуля"}
                          </span>
                          <strong>{lesson.title}</strong>
                          <p>{lesson.summary}</p>
                        </div>
                        <div className="content-lesson-actions">
                          <Link
                            className="button button-ghost button-small"
                            href={`/courses/${selectedCourse.id}/lessons/${lesson.id}`}
                          >
                            <ExternalLink size={15} /> Открыть
                          </Link>
                          <button
                            className="button button-ghost button-small"
                            onClick={() => downloadLessonJson(lesson)}
                          >
                            <Download size={15} /> JSON
                          </button>
                          <button
                            className="button button-danger button-small"
                            disabled={contentBusy}
                            onClick={() => deleteLesson(lesson)}
                          >
                            <Trash2 size={15} /> Удалить
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {activeTab === "reports" && (
        <div className="moderation-layout">
          <div className="moderation-list">
            {reportPanel === "reports" && busy && reports.length === 0 ? (
              <div className="loading-card">
                <span className="loader" /> {t("moderation.loading")}
              </div>
            ) : reportPanel === "numbers" && busy && numbers.length === 0 ? (
              <div className="loading-card">
                <span className="loader" /> Загружаем номера...
              </div>
            ) : reportPanel === "reports" && reports.length === 0 ? (
              <div className="panel-empty moderation-empty">
                <FileSearch />
                <p>{t("moderation.empty")}</p>
              </div>
            ) : reportPanel === "numbers" && numbers.length === 0 ? (
              <div className="panel-empty moderation-empty">
                <BadgeCheck />
                <p>В этом статусе номеров пока нет.</p>
              </div>
            ) : reportPanel === "reports" ? (
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
                    setSelectedNumber(null);
                    setComment(report.moderator_comment || "");
                    setError("");
                  }}
                >
                  <span className="moderation-item-icon">
                    <AlertTriangle />
                  </span>
                  <div>
                    <strong>{report.phone_masked}</strong>
                    <p>{getScamLabel(report.scam_type, language)}</p>
                    <small>
                      #{report.id.slice(0, 8)} ·{" "}
                      {new Date(report.created_at).toLocaleDateString(
                        language === "uz" ? "uz-UZ" : "ru-RU",
                      )}
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
                      ? t("status.approved")
                      : report.status === "rejected"
                        ? t("status.rejected")
                        : t("moderation.awaiting")}
                  </StatusPill>
                </button>
              ))
            ) : (
              numbers.map((number) => (
                <button
                  key={number.number_id}
                  className={
                    selectedNumber?.number_id === number.number_id
                      ? "moderation-list-item active"
                      : "moderation-list-item"
                  }
                  onClick={() => {
                    setSelectedNumber(number);
                    setSelected(null);
                    setError("");
                  }}
                >
                  <span className="moderation-item-icon number-icon">
                    <BadgeCheck />
                  </span>
                  <div>
                    <strong>{number.phone_masked}</strong>
                    <p>{getNumberStatusLabel(number.status)}</p>
                    <small>
                      {number.approved_reports_count} одобренных жалоб
                      {number.last_reported_at
                        ? ` · ${new Date(number.last_reported_at).toLocaleDateString(
                            language === "uz" ? "uz-UZ" : "ru-RU",
                          )}`
                        : ""}
                    </small>
                  </div>
                  <StatusPill
                    tone={
                      number.status === "verified_scammer"
                        ? "danger"
                        : number.status === "scammer"
                          ? "danger"
                          : number.status === "suspicious"
                            ? "warning"
                            : "neutral"
                    }
                  >
                    {getNumberStatusLabel(number.status)}
                  </StatusPill>
                </button>
              ))
            )}
          </div>

          <aside className="moderation-detail">
            {reportPanel === "reports" && !selected ? (
              <div className="moderation-placeholder">
                <FileSearch />
                <h2>{t("moderation.select")}</h2>
                <p>{t("moderation.selectText")}</p>
              </div>
            ) : reportPanel === "numbers" && !selectedNumber ? (
              <div className="moderation-placeholder">
                <BadgeCheck />
                <h2>Выберите номер</h2>
                <p>Здесь появятся статус, жалобы и действие подтверждения.</p>
              </div>
            ) : reportPanel === "reports" && selected ? (
              <>
                <div className="moderation-detail-head">
                  <div>
                    <span className="eyebrow">
                      {t("moderation.report", {
                        id: selected.id.slice(0, 8),
                      })}
                    </span>
                    <h2>{selected.phone_masked}</h2>
                  </div>
                  <button
                    className="detail-close"
                    onClick={() => setSelected(null)}
                    aria-label={t("moderation.close")}
                  >
                    <X />
                  </button>
                </div>

                <div className="number-state">
                  <div>
                    <span>{t("moderation.numberStatus")}</span>
                    <strong>{getNumberStatusLabel(selected.number_status)}</strong>
                  </div>
                  <div>
                    <span>{t("moderation.approvedReports")}</span>
                    <strong>{selected.approved_reports_count}</strong>
                  </div>
                </div>

                <dl className="report-facts">
                  <div>
                    <dt>{t("moderation.scamType")}</dt>
                    <dd>
                      {getScamLabel(selected.scam_type, language)}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.incidentDate")}</dt>
                    <dd>
                      {new Date(selected.incident_date).toLocaleDateString(
                        language === "uz" ? "uz-UZ" : "ru-RU",
                      )}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.region")}</dt>
                    <dd>
                      {regionLabels[selected.region] || selected.region}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.damage")}</dt>
                    <dd>
                      {selected.damage_amount
                        ? `${Number(selected.damage_amount).toLocaleString(
                            language === "uz" ? "uz-UZ" : "ru-RU",
                          )} UZS`
                        : t("moderation.notSpecified")}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.reporter")}</dt>
                    <dd>{selected.reporter_name || t("moderation.noName")}</dd>
                  </div>
                </dl>

                <div className="report-story">
                  <strong>{t("moderation.story")}</strong>
                  <p>{selected.story}</p>
                </div>

                <label className="moderator-comment-field">
                  {t("moderation.comment")}
                  <textarea
                    value={comment}
                    onChange={(event) => setComment(event.target.value)}
                    maxLength={500}
                    placeholder={t("moderation.commentPlaceholder")}
                  />
                </label>

                {selected.status === "pending" ? (
                  <div className="moderation-actions">
                    <button
                      className="button moderation-reject"
                      disabled={busy}
                      onClick={() => moderate("rejected")}
                    >
                      <XCircle size={17} /> {t("moderation.reject")}
                    </button>
                    <button
                      className="button moderation-approve"
                      disabled={busy}
                      onClick={() => moderate("approved")}
                    >
                      <Check size={17} /> {t("moderation.approve")}
                    </button>
                  </div>
                ) : (
                  <div className="decision-banner">
                    {t("moderation.decision")}{" "}
                    <strong>
                      {selected.status === "approved"
                        ? t("moderation.decisionApproved")
                        : t("moderation.decisionRejected")}
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
                    ? t("moderation.unverify")
                    : t("moderation.verify")}
                </button>
              </>
            ) : selectedNumber ? (
              <>
                <div className="moderation-detail-head">
                  <div>
                    <span className="eyebrow">Реестр номеров</span>
                    <h2>{selectedNumber.phone_masked}</h2>
                  </div>
                  <button
                    className="detail-close"
                    onClick={() => setSelectedNumber(null)}
                    aria-label="Закрыть номер"
                  >
                    <X />
                  </button>
                </div>

                <div className="number-state">
                  <div>
                    <span>{t("moderation.numberStatus")}</span>
                    <strong>{getNumberStatusLabel(selectedNumber.status)}</strong>
                  </div>
                  <div>
                    <span>{t("moderation.approvedReports")}</span>
                    <strong>{selectedNumber.approved_reports_count}</strong>
                  </div>
                </div>

                <dl className="report-facts">
                  <div>
                    <dt>Типы схем</dt>
                    <dd>
                      {selectedNumber.scam_types.length
                        ? selectedNumber.scam_types
                            .map((type) => getScamLabel(type, language))
                            .join(", ")
                        : "Пока нет одобренных жалоб"}
                    </dd>
                  </div>
                  <div>
                    <dt>Последняя жалоба</dt>
                    <dd>
                      {selectedNumber.last_reported_at
                        ? new Date(selectedNumber.last_reported_at).toLocaleDateString(
                            language === "uz" ? "uz-UZ" : "ru-RU",
                          )
                        : "Нет данных"}
                    </dd>
                  </div>
                </dl>

                <div className="report-story number-reports">
                  <strong>Последние заявки по номеру</strong>
                  {selectedNumber.latest_reports.length ? (
                    <div className="number-report-list">
                      {selectedNumber.latest_reports.map((report) => (
                        <article key={report.id}>
                          <span>
                            #{report.id.slice(0, 8)} ·{" "}
                            {getScamLabel(report.scam_type, language)}
                          </span>
                          <p>{report.story}</p>
                        </article>
                      ))}
                    </div>
                  ) : (
                    <p>Заявок пока нет.</p>
                  )}
                </div>

                <button
                  className={
                    selectedNumber.number_verified
                      ? "button button-ghost button-wide"
                      : "button button-danger button-wide"
                  }
                  disabled={busy}
                  onClick={toggleVerification}
                >
                  <BadgeCheck size={17} />
                  {selectedNumber.number_verified
                    ? t("moderation.unverify")
                    : t("moderation.verify")}
                </button>
              </>
            ) : null}
          </aside>
        </div>
        )}
      </div>
    </section>
  );
}
