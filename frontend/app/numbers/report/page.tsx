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
import { api } from "@/lib/api";
import { regions, scamTypes } from "@/lib/scam-data";

type CreatedReport = {
  id: string;
  phone_masked: string;
  scam_type: string;
  status: "pending";
  created_at: string;
};

export default function ReportNumberPage() {
  const { user, loading } = useAuth();
  const [phone, setPhone] = useState("+998");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [created, setCreated] = useState<CreatedReport | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
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
            incident_date: form.get("incident_date"),
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
          <span className="loader" /> Проверяем авторизацию...
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="page-section report-number-page">
        <div className="container narrow-container">
          <Link href="/numbers" className="back-link">
            <ArrowLeft size={17} /> Проверка номеров
          </Link>
          <div className="empty-state">
            <span className="empty-icon">
              <LockKeyhole />
            </span>
            <h1>Войдите, чтобы подать заявку</h1>
            <p>
              Авторизация защищает базу от анонимного спама. Ваш номер телефона
              не отображается в публичной заявке.
            </p>
            <Link
              className="button button-primary"
              href="/login?next=/numbers/report"
            >
              Войти по номеру телефона
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
            <span className="eyebrow">Заявка зарегистрирована</span>
            <h1>Номер отправлен на проверку</h1>
            <p>
              Заявка <strong>#{created.id.slice(0, 8)}</strong> получила статус
              «На модерации». Номер появится в публичной базе только после
              проверки модератором.
            </p>
            <div className="report-success-details">
              <span>Номер</span>
              <strong>{created.phone_masked}</strong>
              <span>Статус</span>
              <strong>На модерации</strong>
            </div>
            <div className="result-actions">
              <Link className="button button-primary" href="/account">
                Мои заявки
              </Link>
              <button
                className="button button-ghost"
                onClick={() => {
                  setCreated(null);
                  setPhone("+998");
                }}
              >
                Подать ещё одну
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
        <Link href="/numbers" className="back-link">
          <ArrowLeft size={17} /> Проверка номеров
        </Link>

        <div className="report-page-grid">
          <div className="report-page-intro">
            <span className="eyebrow">
              <FilePlus2 size={16} /> Заявка гражданина
            </span>
            <h1>Сообщить о мошенническом номере</h1>
            <p>
              Укажите, что произошло. После модерации подтверждённая жалоба
              повлияет на статус номера в публичной базе CyberSafe.
            </p>
            <div className="report-process">
              <div>
                <span>1</span>
                <p>
                  <strong>Вы отправляете заявку</strong>
                  Номер сразу не публикуется.
                </p>
              </div>
              <div>
                <span>2</span>
                <p>
                  <strong>Модератор проверяет сведения</strong>
                  Дубли и спам отклоняются.
                </p>
              </div>
              <div>
                <span>3</span>
                <p>
                  <strong>База обновляется</strong>
                  Одобренная жалоба учитывается в статусе номера.
                </p>
              </div>
            </div>
            <div className="privacy-callout">
              <ShieldCheck />
              <p>
                В публичной базе не показываются ваше имя и номер телефона. Не
                указывайте в описании паспортные данные, SMS-коды или пароли.
              </p>
            </div>
          </div>

          <form className="report-number-form" onSubmit={submit}>
            <h2>Данные о происшествии</h2>
            <label>
              Номер мошенника
              <input
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                placeholder="+998 90 123 45 67"
                required
              />
              <small>Формат: +998XXXXXXXXX</small>
            </label>
            <label>
              Вид мошенничества
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
                Дата происшествия
                <input
                  name="incident_date"
                  type="date"
                  max={new Date().toISOString().slice(0, 10)}
                  required
                />
              </label>
              <label>
                Регион
                <select name="region" defaultValue="" required>
                  <option value="" disabled>
                    Выберите регион
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
              Описание ситуации
              <textarea
                name="story"
                minLength={20}
                maxLength={1000}
                placeholder="Например: позвонили от имени банка, сообщили о подозрительном переводе и попросили назвать код из SMS..."
                required
              />
              <small>Минимум 20 символов, максимум 1000.</small>
            </label>
            <label>
              Сумма ущерба в сумах
              <input
                name="damage_amount"
                type="number"
                min="0"
                step="0.01"
                placeholder="Необязательно"
              />
            </label>

            <div className="report-warning">
              <AlertTriangle />
              <p>
                Если деньги уже списаны, сначала заблокируйте карту и сообщите
                о происшествии своему банку.
              </p>
            </div>
            {error && <div className="form-error">{error}</div>}
            <button
              className="button button-primary button-wide"
              disabled={busy}
            >
              <Send size={17} />
              {busy ? "Отправляем..." : "Отправить на модерацию"}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
