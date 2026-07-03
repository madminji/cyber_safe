"use client";

import { Award, Download, ExternalLink, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { Certificate } from "@/lib/types";

export default function CertificatesPage() {
  const { user, loading } = useAuth();
  const { language, t } = useLanguage();
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  const downloadPdf = async (certificate: Certificate) => {
    setError("");
    try {
      const access = localStorage.getItem("cybersafe_access");
      const response = await fetch(certificate.pdf_url, {
        headers: access ? { Authorization: `Bearer ${access}` } : {},
      });
      if (!response.ok) throw new Error(t("cert.downloadError"));
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `cybersafe-${certificate.id}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      setError((requestError as Error).message);
    }
  };

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
            <Award size={15} /> {t("cert.eyebrow")}
          </span>
          <h1>{t("cert.title")}</h1>
          <p>{t("cert.lead")}</p>
        </div>

        {!loading && !user ? (
          <div className="empty-state">
            <span className="empty-icon">
              <LockKeyhole />
            </span>
            <h2>{t("cert.loginTitle")}</h2>
            <p>{t("cert.loginText")}</p>
            <Link className="button button-primary" href="/login">
              {t("common.login")}
            </Link>
          </div>
        ) : busy ? (
          <div className="loading-card">
            <span className="loader" /> {t("cert.loading")}
          </div>
        ) : certificates.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">
              <Award />
            </span>
            <h2>{t("cert.emptyTitle")}</h2>
            <p>{t("cert.emptyText")}</p>
            <Link className="button button-primary" href="/quiz">
              {t("cert.takeQuiz")}
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
                <p>{t("cert.level")}</p>
                <strong>{certificate.level.toUpperCase()}</strong>
                <div className="certificate-score">{certificate.score}%</div>
                <small>
                  {t("cert.issued")}{" "}
                  {new Date(certificate.issued_at).toLocaleDateString(
                    language === "uz" ? "uz-UZ" : "ru-RU",
                  )}
                </small>
                <div className="certificate-actions">
                  <button
                    className="button button-primary button-small"
                    onClick={() => downloadPdf(certificate)}
                  >
                    <Download size={16} /> PDF
                  </button>
                  <a
                    className="button button-ghost button-small"
                    href={certificate.verification_url}
                    target="_blank"
                  >
                    <ExternalLink size={16} /> {t("cert.verify")}
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
