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
  target_type: string;
  target_display: string;
  phone_masked: string;
  scam_type: string;
  status: "pending";
  created_at: string;
};

const dateInputPattern = /^\d{2}\.\d{2}\.\d{4}$/;

function formatIncidentDateInput(value: string) {
  const digits = value.replace(/\D/g, "").slice(0, 8);
  const day = digits.slice(0, 2);
  const month = digits.slice(2, 4);
  const year = digits.slice(4, 8);
  return [day, month, year].filter(Boolean).join(".");
}

function toIsoDate(value: string) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const date = new Date(`${value}T00:00:00`);
    const today = new Date();
    today.setHours(23, 59, 59, 999);
    return date > today ? null : value;
  }
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
  const [targetType, setTargetType] = useState<
    "phone" | "url" | "account" | "card" | "other"
  >("phone");
  const [targetValue, setTargetValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [created, setCreated] = useState<CreatedReport | null>(null);
  const [incidentDate, setIncidentDate] = useState("");
  const scamTypes = getScamTypes(language);
  const regions = getRegions(language);
  const dateCopy = {
    ru: {
      invalid:
        "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0434\u0430\u0442\u0443 \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 \u0414\u0414.\u041c\u041c.\u0413\u0413\u0413\u0413. \u0414\u0430\u0442\u0430 \u043d\u0435 \u0434\u043e\u043b\u0436\u043d\u0430 \u0431\u044b\u0442\u044c \u0432 \u0431\u0443\u0434\u0443\u0449\u0435\u043c.",
      format: "\u0424\u043e\u0440\u043c\u0430\u0442: \u0414\u0414.\u041c\u041c.\u0413\u0413\u0413\u0413",
      placeholder: "\u0414\u0414.\u041c\u041c.\u0413\u0413\u0413\u0413",
    },
    uz: {
      invalid:
        "Sanani KK.OO.YYYY formatida kiriting. Kelajak sanasini kiritmang.",
      format: "Format: KK.OO.YYYY",
      placeholder: "KK.OO.YYYY",
    },
  }[language];
  const targetCopy = {
    ru: {
      targetType: "\u041e \u0447\u0451\u043c \u0437\u0430\u044f\u0432\u043a\u0430",
      target: "\u041f\u043e\u0434\u043e\u0437\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043e\u0431\u044a\u0435\u043a\u0442",
      phone: "\u0422\u0435\u043b\u0435\u0444\u043e\u043d\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440",
      url: "\u0421\u0430\u0439\u0442 \u0438\u043b\u0438 \u0441\u0441\u044b\u043b\u043a\u0430",
      account: "Telegram / \u0430\u043a\u043a\u0430\u0443\u043d\u0442",
      card: "\u041a\u0430\u0440\u0442\u0430 \u0438\u043b\u0438 \u0441\u0447\u0451\u0442",
      other: "\u0414\u0440\u0443\u0433\u043e\u0435",
      placeholders: {
        phone: "+998 90 123 45 67",
        url: "https://example.com",
        account: "@username, Telegram ID \u0438\u043b\u0438 \u043f\u0440\u043e\u0444\u0438\u043b\u044c",
        card: "\u041d\u043e\u043c\u0435\u0440 \u043a\u0430\u0440\u0442\u044b/\u0441\u0447\u0451\u0442\u0430, \u0435\u0441\u043b\u0438 \u043e\u043d \u0443 \u0432\u0430\u0441 \u0435\u0441\u0442\u044c",
        other: "\u041e\u043f\u0438\u0448\u0438\u0442\u0435 \u043e\u0431\u044a\u0435\u043a\u0442: email, \u043d\u0438\u043a, \u0441\u0435\u0440\u0432\u0438\u0441...",
      },
      phoneHint:
        "\u0422\u0435\u043b\u0435\u0444\u043e\u043d\u043d\u044b\u0435 \u0436\u0430\u043b\u043e\u0431\u044b \u043f\u043e\u0441\u043b\u0435 \u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0438\u044f \u043f\u043e\u043f\u0430\u0434\u0430\u044e\u0442 \u0432 \u0431\u0430\u0437\u0443 \u043d\u043e\u043c\u0435\u0440\u043e\u0432.",
      generalHint:
        "\u042d\u0442\u0430 \u0437\u0430\u044f\u0432\u043a\u0430 \u043f\u043e\u043f\u0430\u0434\u0451\u0442 \u0432 \u043c\u043e\u0434\u0435\u0440\u0430\u0446\u0438\u044e, \u043d\u043e \u043d\u0435 \u0432 \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u0443\u044e \u0431\u0430\u0437\u0443 \u043d\u043e\u043c\u0435\u0440\u043e\u0432.",
    },
    uz: {
      targetType: "Ariza nimaga tegishli",
      target: "Shubhali obyekt",
      phone: "Telefon raqami",
      url: "Sayt yoki havola",
      account: "Telegram / akkaunt",
      card: "Karta yoki hisob",
      other: "Boshqa",
      placeholders: {
        phone: "+998 90 123 45 67",
        url: "https://example.com",
        account: "@username, Telegram ID yoki profil",
        card: "Karta/hisob raqami, agar sizda bo\u2018lsa",
        other: "Obyektni yozing: email, nik, servis...",
      },
      phoneHint:
        "Telefon bo\u2018yicha shikoyatlar tasdiqlangandan keyin raqamlar bazasiga tushadi.",
      generalHint:
        "Bu ariza moderatsiyaga tushadi, lekin ommaviy raqamlar bazasiga kiritilmaydi.",
    },
  }[language];

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const incidentDateIso = toIsoDate(incidentDate);
    if (!incidentDateIso) {
      setError(dateCopy.invalid);
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
            phone: targetType === "phone" ? phone : undefined,
            target_type: targetType,
            target_value: targetType === "phone" ? phone : targetValue,
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
              <strong>{created.target_display || created.phone_masked}</strong>
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
                  setTargetType("phone");
                  setTargetValue("");
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
              {targetCopy.targetType}
              <select
                value={targetType}
                onChange={(event) =>
                  setTargetType(
                    event.target.value as
                      | "phone"
                      | "url"
                      | "account"
                      | "card"
                      | "other",
                  )
                }
              >
                <option value="phone">{targetCopy.phone}</option>
                <option value="url">{targetCopy.url}</option>
                <option value="account">{targetCopy.account}</option>
                <option value="card">{targetCopy.card}</option>
                <option value="other">{targetCopy.other}</option>
              </select>
            </label>
            <label>
              {targetCopy.target}
              <input
                value={targetType === "phone" ? phone : targetValue}
                onChange={(event) =>
                  targetType === "phone"
                    ? setPhone(event.target.value)
                    : setTargetValue(event.target.value)
                }
                placeholder={targetCopy.placeholders[targetType]}
                required
              />
              <small>
                {targetType === "phone" ? targetCopy.phoneHint : targetCopy.generalHint}
              </small>
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
                  placeholder={dateCopy.placeholder}
                  type="text"
                  value={incidentDate}
                  onChange={(event) =>
                    setIncidentDate(formatIncidentDateInput(event.target.value))
                  }
                  required
                />
                <small>
                  {dateCopy.format}
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
