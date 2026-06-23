"use client";

import { Award, Download, ExternalLink, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { API_URL, api } from "@/lib/api";
import { Certificate } from "@/lib/types";

export default function CertificatesPage() {
  const { user, loading } = useAuth();
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (loading) return;
    if (!user) {
      setBusy(false);
      return;
    }
    api<Certificate[]>("/certificates/", { auth: true })
      .then(setCertificates)
      .catch((requestError) => setError(requestError.message))
      .finally(() => setBusy(false));
  }, [user, loading]);

  return (
    <section className="page-section certificates-page">
      <div className="container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <Award size={15} /> Подтверждение знаний
          </span>
          <h1>Мои сертификаты</h1>
          <p>Каждый документ имеет уникальный ID и публичную QR-проверку.</p>
        </div>

        {!loading && !user ? (
          <div className="empty-state">
            <span className="empty-icon">
              <LockKeyhole />
            </span>
            <h2>Войдите, чтобы увидеть сертификаты</h2>
            <p>Сертификат сохраняется в кабинете после успешного теста.</p>
            <Link className="button button-primary" href="/login">
              Войти
            </Link>
          </div>
        ) : busy ? (
          <div className="loading-card">
            <span className="loader" /> Загружаем сертификаты...
          </div>
        ) : certificates.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">
              <Award />
            </span>
            <h2>Здесь появится ваш первый сертификат</h2>
            <p>Наберите не менее 60% в тесте по цифровой безопасности.</p>
            <Link className="button button-primary" href="/quiz">
              Пройти тест
            </Link>
          </div>
        ) : (
          <div className="certificate-grid">
            {certificates.map((certificate) => (
              <article className="certificate-card" key={certificate.id}>
                <div className="certificate-pattern" />
                <div className="certificate-seal">
                  <Award />
                </div>
                <span>CYBERSAFE UZBEKISTAN</span>
                <h2>{certificate.owner_name}</h2>
                <p>Уровень цифровой безопасности</p>
                <strong>{certificate.level.toUpperCase()}</strong>
                <div className="certificate-score">{certificate.score}%</div>
                <small>
                  Выдан {new Date(certificate.issued_at).toLocaleDateString("ru-RU")}
                </small>
                <div className="certificate-actions">
                  <a
                    className="button button-primary button-small"
                    href={`${API_URL}/certificates/${certificate.id}/pdf/`}
                    target="_blank"
                  >
                    <Download size={16} /> PDF
                  </a>
                  <a
                    className="button button-ghost button-small"
                    href={`${API_URL}/certificates/${certificate.id}/`}
                    target="_blank"
                  >
                    <ExternalLink size={16} /> Проверить
                  </a>
                </div>
              </article>
            ))}
          </div>
        )}
        {error && <div className="form-error centered">{error}</div>}
      </div>
    </section>
  );
}

