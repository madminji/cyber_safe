"use client";

import {
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
  ClipboardPaste,
  ExternalLink,
  FileWarning,
  Link2,
  LockKeyhole,
  MessageSquareText,
  PhoneCall,
  SearchCheck,
  ShieldQuestion,
} from "lucide-react";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { getScamLabel } from "@/lib/scam-data";
import { AnalysisResult, NumberCheck } from "@/lib/types";

type Mode = "url" | "sms" | "phone";

export default function AnalyzerPage() {
  const { language, t } = useLanguage();
  const [mode, setMode] = useState<Mode>("url");
  const [value, setValue] = useState("");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null,
  );
  const [numberResult, setNumberResult] = useState<NumberCheck | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (window.location.hash === "#phone") {
      setMode("phone");
      setValue("+998");
    }
  }, []);

  const switchMode = (next: Mode) => {
    setMode(next);
    setValue(next === "phone" ? "+998" : "");
    setAnalysisResult(null);
    setNumberResult(null);
    setError("");
    window.history.replaceState(null, "", next === "phone" ? "#phone" : "#");
  };

  const analyze = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    setAnalysisResult(null);
    setNumberResult(null);
    try {
      if (mode === "phone") {
        setNumberResult(
          await api<NumberCheck>(
            `/scammer-db/check/?phone=${encodeURIComponent(value)}`,
          ),
        );
        return;
      }
      const payload =
        mode === "url"
          ? { url: value, language }
          : { text: value, language };
      setAnalysisResult(
        await api<AnalysisResult>(`/analyzer/${mode}/`, {
          method: "POST",
          body: JSON.stringify(payload),
        }),
      );
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const verdictContent = {
    safe: {
      label: t("analyzer.safe"),
      description: t("analyzer.safeDescription"),
      icon: <CheckCircle2 />,
    },
    suspicious: {
      label: t("analyzer.suspicious"),
      description: t("analyzer.suspiciousDescription"),
      icon: <ShieldQuestion />,
    },
    dangerous: {
      label: t("analyzer.dangerous"),
      description: t("analyzer.dangerousDescription"),
      icon: <AlertOctagon />,
    },
  };

  return (
    <section className="page-section analyzer-page">
      <div className="container analyzer-container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <SearchCheck size={15} /> {t("analyzer.eyebrow")}
          </span>
          <h1>{t("analyzer.title")}</h1>
          <p>{t("analyzer.lead")}</p>
        </div>

        <div className="analyzer-card">
          <div className="analyzer-tabs">
            <button
              className={mode === "url" ? "active" : ""}
              onClick={() => switchMode("url")}
            >
              <Link2 size={18} /> {t("analyzer.urlTab")}
            </button>
            <button
              className={mode === "sms" ? "active" : ""}
              onClick={() => switchMode("sms")}
            >
              <MessageSquareText size={18} /> {t("analyzer.smsTab")}
            </button>
            <button
              className={mode === "phone" ? "active" : ""}
              onClick={() => switchMode("phone")}
            >
              <PhoneCall size={18} /> {t("analyzer.phoneTab")}
            </button>
          </div>

          <form onSubmit={analyze} className="analyzer-form">
            <label>
              {mode === "url"
                ? t("analyzer.urlLabel")
                : mode === "sms"
                  ? t("analyzer.smsLabel")
                  : t("analyzer.phoneLabel")}
            </label>
            {mode === "url" || mode === "phone" ? (
              <div className="analyzer-input">
                {mode === "url" ? (
                  <ExternalLink size={20} />
                ) : (
                  <PhoneCall size={20} />
                )}
                <input
                  value={value}
                  onChange={(event) => setValue(event.target.value)}
                  placeholder={
                    mode === "url"
                      ? "https://example.com/login"
                      : "+998 90 123 45 67"
                  }
                  required
                />
              </div>
            ) : (
              <textarea
                value={value}
                onChange={(event) => setValue(event.target.value)}
                placeholder={t("analyzer.smsPlaceholder")}
                minLength={3}
                maxLength={5000}
                required
              />
            )}
            {mode !== "phone" && (
              <div className="analyzer-form-footer">
                <button
                  type="button"
                  className="example-button"
                  onClick={() =>
                    setValue(
                      mode === "url"
                        ? "http://payme.uz@192.168.1.10/secure/login"
                        : t("analyzer.exampleSms"),
                    )
                  }
                >
                  <ClipboardPaste size={15} /> {t("analyzer.example")}
                </button>
                <span>
                  {value.length} {t("analyzer.characters")}
                </span>
              </div>
            )}
            {error && <div className="form-error">{error}</div>}
            <button
              className="button button-primary button-wide"
              disabled={busy || !value.trim()}
            >
              <SearchCheck size={18} />
              {busy
                ? t("analyzer.analyzing")
                : mode === "phone"
                  ? t("numbers.check")
                  : t("analyzer.submit")}
            </button>
          </form>
        </div>

        {analysisResult && (
          <div className={`analysis-result ${analysisResult.verdict}`}>
            <div className="analysis-summary">
              <div className="risk-gauge">
                <svg viewBox="0 0 120 120" aria-hidden="true">
                  <circle cx="60" cy="60" r="50" />
                  <circle
                    className="gauge-value"
                    cx="60"
                    cy="60"
                    r="50"
                    style={{
                      strokeDashoffset:
                        314 - (314 * analysisResult.risk_score) / 100,
                    }}
                  />
                </svg>
                <strong>{analysisResult.risk_score}</strong>
                <small>{t("analyzer.outOf")}</small>
              </div>
              <div>
                <span className="analysis-verdict-icon">
                  {verdictContent[analysisResult.verdict].icon}
                </span>
                <h2>{verdictContent[analysisResult.verdict].label}</h2>
                <p>{verdictContent[analysisResult.verdict].description}</p>
              </div>
            </div>
            <div className="analysis-reasons">
              <h3>{t("analyzer.found")}</h3>
              {analysisResult.reasons.map((reason, index) => (
                <div key={`${reason}-${index}`}>
                  <span>{index + 1}</span>
                  <p>{reason}</p>
                </div>
              ))}
            </div>
            <div className="privacy-strip">
              <LockKeyhole size={17} />
              {analysisResult.privacy}
            </div>
          </div>
        )}

        {numberResult && (
          <div
            className={`number-result ${
              numberResult.status === "verified_scammer" ||
              numberResult.status === "scammer"
                ? "danger"
                : numberResult.status === "suspicious"
                  ? "warning"
                  : "neutral"
            }`}
          >
            <div className="number-result-icon">
              {numberResult.found ? <AlertTriangle /> : <ShieldQuestion />}
            </div>
            <div className="number-result-main">
              <StatusPill
                tone={
                  numberResult.status === "verified_scammer" ||
                  numberResult.status === "scammer"
                    ? "danger"
                    : numberResult.status === "suspicious"
                      ? "warning"
                      : "neutral"
                }
              >
                {numberResult.status === "not_found"
                  ? t("numbers.notFound")
                  : numberResult.status === "suspicious"
                    ? t("numbers.suspicious")
                    : numberResult.status === "verified_scammer"
                      ? t("numbers.verified")
                      : t("numbers.highRisk")}
              </StatusPill>
              <h2>{numberResult.phone_masked || value}</h2>
              {numberResult.found ? (
                <>
                  <p>
                    {t("numbers.confirmedReports")}{" "}
                    <strong>{numberResult.approved_reports_count}</strong>
                  </p>
                  <div className="tag-list">
                    {numberResult.scam_types?.map((type) => (
                      <span key={type}>{getScamLabel(type, language)}</span>
                    ))}
                  </div>
                </>
              ) : (
                <p>{t("numbers.noApproved")}</p>
              )}
            </div>
            <Link className="button button-danger" href="/numbers/report">
              <FileWarning size={17} /> {t("numbers.reportNumber")}
            </Link>
          </div>
        )}

        {numberResult?.reports && numberResult.reports.length > 0 && (
          <div className="story-section">
            <h2>{t("numbers.stories")}</h2>
            <div className="story-grid">
              {numberResult.reports.map((report, index) => (
                <article className="story-card" key={`${report.story}-${index}`}>
                  <div>
                    <StatusPill tone="warning">
                      {getScamLabel(report.scam_type, language)}
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

        <div className="analyzer-disclaimer">
          <ShieldQuestion />
          <p>{t("analyzer.disclaimer")}</p>
        </div>
      </div>
    </section>
  );
}
