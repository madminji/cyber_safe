"use client";

import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  FilePlus2,
  LockKeyhole,
  Send,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { getRegions, getScamTypes } from "@/lib/scam-data";

type CreatedReport = {
  id: string;
  phone_masked: string;
  scam_type: string;
  status: "pending";
  created_at: string;
};

const dateInputPattern = /^\d{2}\.\d{2}\.\d{4}$/;

function toIsoDate(value: string) {
  if (!dateInputPattern.test(value)) return null;
  const [day, month, year] = value.split(".").map(Number);
  const date = new Date(year, month - 1, day);
  if (
    date.getFullYear() !== year ||
    date.getMonth() !== month - 1 ||
    date.getDate() !== day
  ) {
    return null;
  }
  const today = new Date();
  today.setHours(23, 59, 59, 999);
  if (date > today) return null;
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(
    2,
    "0",
  )}`;
}

export default function ReportNumberPage() {
  const { user, loading } = useAuth();
  const { language, t } = useLanguage();
  const [phone, setPhone] = useState("+998");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [created, setCreated] = useState<CreatedReport | null>(null);
  const [incidentDate, setIncidentDate] = useState("");
  const scamTypes = getScamTypes(language);
  const regions = getRegions(language);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const incidentDateIso = toIsoDate(incidentDate);
    if (!incidentDateIso) {
      setError(
        language === "uz"
          ? "Sanani KK.OO.YYYY formatida kiriting. Kelajak sanasini kiritmang."
          : "Введите дату в формате ДД.ММ.ГГГГ. Дата не должна быть в будущем.",
      );
      return;
    }
    setBusy(true);
    setError("");
    try {
      setCreated(
        await api<CreatedReport>("/scammer-db/reports/", {
          method: "POST",
          auth: true,
          body: JSON.stringify({
            phone,
            scam_type: form.get("scam_type"),
            incident_date: incidentDateIso,
            story: form.get("story"),
            region: form.get("region"),
            damage_amount: form.get("damage_amount") || null,
          }),
        }),
      );
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
          <span className="loader" /> {t("report.authChecking")}
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="page-section report-number-page">
        <div className="container narrow-container">
          <Link href="/analyzer#phone" className="back-link">
            <ArrowLeft size={17} /> {t("report.numbers")}
          </Link>
          <div className="empty-state">
            <span className="empty-icon">
              <LockKeyhole />
            </span>
            <h1>{t("report.loginTitle")}</h1>
            <p>{t("report.loginText")}</p>
            <Link
              className="button button-primary"
              href="/login?next=/numbers/report"
            >
              {t("report.loginButton")}
            </Link>
          </div>
        </div>
      </section>
    );
  }

  if (created) {
    return (
      <section className="page-section report-number-page">
        <div className="container narrow-container">
          <div className="report-success-card">
            <span className="report-success-icon">
              <CheckCircle2 />
            </span>
            <span className="eyebrow">{t("report.registered")}</span>
            <h1>{t("report.sentTitle")}</h1>
            <p>{t("report.sentText", { id: created.id.slice(0, 8) })}</p>
            <div className="report-success-details">
              <span>{t("report.number")}</span>
              <strong>{created.phone_masked}</strong>
              <span>{t("report.status")}</span>
              <strong>{t("report.moderation")}</strong>
            </div>
            <div className="result-actions">
              <Link className="button button-primary" href="/account">
                {t("report.my")}
              </Link>
              <button
                className="button button-ghost"
                onClick={() => {
                  setCreated(null);
                  setPhone("+998");
                  setIncidentDate("");
                }}
              >
                {t("report.another")}
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="page-section report-number-page">
      <div className="container report-form-container">
        <Link href="/analyzer#phone" className="back-link">
          <ArrowLeft size={17} /> {t("report.numbers")}
        </Link>

        <div className="report-page-grid">
          <div className="report-page-intro">
            <span className="eyebrow">
              <FilePlus2 size={16} /> {t("report.eyebrow")}
            </span>
            <h1>{t("report.title")}</h1>
            <p>{t("report.lead")}</p>
            <div className="report-process">
              <div>
                <span>1</span>
                <p>
                  <strong>{t("report.step1Title")}</strong>
                  {t("report.step1Text")}
                </p>
              </div>
              <div>
                <span>2</span>
                <p>
                  <strong>{t("report.step2Title")}</strong>
                  {t("report.step2Text")}
                </p>
              </div>
              <div>
                <span>3</span>
                <p>
                  <strong>{t("report.step3Title")}</strong>
                  {t("report.step3Text")}
                </p>
              </div>
            </div>
            <div className="privacy-callout">
              <ShieldCheck />
              <p>{t("report.privacy")}</p>
            </div>
          </div>

          <form className="report-number-form" onSubmit={submit}>
            <h2>{t("report.details")}</h2>
            <label>
              {t("report.scammerNumber")}
              <input
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                placeholder="+998 90 123 45 67"
                required
              />
              <small>{t("report.format")}</small>
            </label>
            <label>
              {t("report.scamType")}
              <select name="scam_type" defaultValue="bank_call" required>
                {scamTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </label>
            <div className="form-row">
              <label>
                {t("report.incidentDate")}
                <input
                  inputMode="numeric"
                  pattern="\d{2}\.\d{2}\.\d{4}"
                  placeholder={language === "uz" ? "24.06.2026" : "24.06.2026"}
                  value={incidentDate}
                  onChange={(event) => setIncidentDate(event.target.value)}
                  required
                />
                <small>
                  {language === "uz"
                    ? "Format: KK.OO.YYYY"
                    : "Формат: ДД.ММ.ГГГГ"}
                </small>
              </label>
              <label>
                {t("report.region")}
                <select name="region" defaultValue="" required>
                  <option value="" disabled>
                    {t("report.selectRegion")}
                  </option>
                  {regions.map((region) => (
                    <option key={region.value} value={region.value}>
                      {region.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label>
              {t("report.description")}
              <textarea
                name="story"
                minLength={20}
                maxLength={1000}
                placeholder={t("report.descriptionPlaceholder")}
                required
              />
              <small>{t("report.descriptionLimit")}</small>
            </label>
            <label>
              {t("report.damage")}
              <input
                name="damage_amount"
                type="number"
                min="0"
                step="0.01"
                placeholder={t("report.optional")}
              />
            </label>

            <div className="report-warning">
              <AlertTriangle />
              <p>{t("report.warning")}</p>
            </div>
            {error && <div className="form-error">{error}</div>}
            <button
              className="button button-primary button-wide"
              disabled={busy}
            >
              <Send size={17} />
              {busy ? t("report.sending") : t("report.submit")}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
