"use client";

import {
  AlertOctagon,
  CheckCircle2,
  ClipboardPaste,
  ExternalLink,
  Link2,
  LockKeyhole,
  MessageSquareText,
  SearchCheck,
  ShieldQuestion,
} from "lucide-react";
import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { AnalysisResult } from "@/lib/types";

type Mode = "url" | "sms";

const examples = {
  url: "http://payme.uz@192.168.1.10/secure/login",
  sms: "Срочно! Ваша карта будет заблокирована. Назовите SMS-код и переведите деньги на безопасный счёт.",
};

export default function AnalyzerPage() {
  const [mode, setMode] = useState<Mode>("url");
  const [value, setValue] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const switchMode = (next: Mode) => {
    setMode(next);
    setValue("");
    setResult(null);
    setError("");
  };

  const analyze = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const payload = mode === "url" ? { url: value } : { text: value };
      setResult(
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
      label: "Явных угроз не найдено",
      description:
        "Автоматическая проверка не обнаружила очевидных признаков обмана. Сохраняйте осторожность.",
      icon: <CheckCircle2 />,
    },
    suspicious: {
      label: "Подозрительно",
      description:
        "Обнаружены признаки, требующие дополнительной проверки. Не переходите по ссылке и не отвечайте отправителю.",
      icon: <ShieldQuestion />,
    },
    dangerous: {
      label: "Высокий риск",
      description:
        "Обнаружено несколько характерных признаков мошенничества. Прекратите взаимодействие.",
      icon: <AlertOctagon />,
    },
  };

  return (
    <section className="page-section analyzer-page">
      <div className="container analyzer-container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <SearchCheck size={15} /> Мгновенная проверка
          </span>
          <h1>Анализатор ссылок и SMS</h1>
          <p>
            Вставьте подозрительный адрес или сообщение. Анализ выполняется без
            открытия ссылки и без сохранения исходного текста.
          </p>
        </div>

        <div className="analyzer-card">
          <div className="analyzer-tabs">
            <button
              className={mode === "url" ? "active" : ""}
              onClick={() => switchMode("url")}
            >
              <Link2 size={18} /> Проверить ссылку
            </button>
            <button
              className={mode === "sms" ? "active" : ""}
              onClick={() => switchMode("sms")}
            >
              <MessageSquareText size={18} /> Проверить SMS
            </button>
          </div>

          <form onSubmit={analyze} className="analyzer-form">
            <label>
              {mode === "url"
                ? "Адрес подозрительного сайта"
                : "Текст сообщения"}
            </label>
            {mode === "url" ? (
              <div className="analyzer-input">
                <ExternalLink size={20} />
                <input
                  value={value}
                  onChange={(event) => setValue(event.target.value)}
                  placeholder="https://example.com/login"
                  required
                />
              </div>
            ) : (
              <textarea
                value={value}
                onChange={(event) => setValue(event.target.value)}
                placeholder="Вставьте сюда полный текст SMS или сообщения..."
                minLength={3}
                maxLength={5000}
                required
              />
            )}
            <div className="analyzer-form-footer">
              <button
                type="button"
                className="example-button"
                onClick={() => setValue(examples[mode])}
              >
                <ClipboardPaste size={15} /> Подставить пример
              </button>
              <span>{value.length} символов</span>
            </div>
            {error && <div className="form-error">{error}</div>}
            <button
              className="button button-primary button-wide"
              disabled={busy || !value.trim()}
            >
              <SearchCheck size={18} />
              {busy ? "Анализируем..." : "Проверить сейчас"}
            </button>
          </form>
        </div>

        {result && (
          <div className={`analysis-result ${result.verdict}`}>
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
                      strokeDashoffset: 314 - (314 * result.risk_score) / 100,
                    }}
                  />
                </svg>
                <strong>{result.risk_score}</strong>
                <small>из 100</small>
              </div>
              <div>
                <span className="analysis-verdict-icon">
                  {verdictContent[result.verdict].icon}
                </span>
                <h2>{verdictContent[result.verdict].label}</h2>
                <p>{verdictContent[result.verdict].description}</p>
              </div>
            </div>
            <div className="analysis-reasons">
              <h3>Что обнаружено</h3>
              {result.reasons.map((reason, index) => (
                <div key={`${reason}-${index}`}>
                  <span>{index + 1}</span>
                  <p>{reason}</p>
                </div>
              ))}
            </div>
            <div className="privacy-strip">
              <LockKeyhole size={17} />
              {result.privacy}
            </div>
          </div>
        )}

        <div className="analyzer-disclaimer">
          <ShieldQuestion />
          <p>
            Анализатор — вспомогательный инструмент, а не гарантия безопасности.
            Не вводите пароли, коды из SMS и банковские данные на сайтах,
            полученных от неизвестных отправителей.
          </p>
        </div>
      </div>
    </section>
  );
}
