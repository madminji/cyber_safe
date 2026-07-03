"use client";

import {
  AlertTriangle,
  Award,
  BadgeCheck,
  CalendarDays,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { Certificate } from "@/lib/types";

export default function CertificateVerifyPage() {
  const params = useParams<{ id: string }>();
  const { language, t } = useLanguage();
  const [certificate, setCertificate] = useState<Certificate | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Certificate>(`/certificates/${params.id}/`)
      .then(setCertificate)
      .catch((requestError) => setError((requestError as Error).message))
      .finally(() => setBusy(false));
  }, [params.id]);

  return (
    <section className="page-section certificate-verify-page">
      <div className="container narrow-container">
        <div className="verify-card">
          <div
            className={
              certificate?.is_valid
                ? "verify-status valid"
                : error
                  ? "verify-status missing"
                  : "verify-status invalid"
            }
          >
            {busy ? (
              <span className="loader" />
            ) : certificate?.is_valid ? (
              <BadgeCheck />
            ) : error ? (
              <XCircle />
            ) : (
              <AlertTriangle />
            )}
          </div>

          {busy ? (
            <>
              <span className="eyebrow">CyberSafe Uzbekistan</span>
              <h1>{t("cert.verifyLoading")}</h1>
              <p>{t("cert.verifyLoadingText")}</p>
            </>
          ) : error ? (
            <>
              <span className="eyebrow">{t("cert.verifyEyebrow")}</span>
              <h1>{t("cert.verifyMissingTitle")}</h1>
              <p>{t("cert.verifyMissingText")}</p>
              <Link className="button button-primary" href="/">
                {t("cert.verifyHome")}
              </Link>
            </>
          ) : certificate ? (
            <>
              <span className="eyebrow">
                <ShieldCheck size={15} /> {t("cert.verifyEyebrow")}
              </span>
              <h1>
                {certificate.is_valid
                  ? t("cert.verifyValid")
                  : t("cert.verifyInvalid")}
              </h1>
              <p>{t("cert.verifyFoundText")}</p>

              <div className="verify-facts">
                <div>
                  <span>{t("cert.owner")}</span>
                  <strong>{certificate.owner_name}</strong>
                </div>
                <div>
                  <span>{t("cert.level")}</span>
                  <strong>{certificate.level.toUpperCase()}</strong>
                </div>
                <div>
                  <span>{t("cert.result")}</span>
                  <strong>{certificate.score}%</strong>
                </div>
                <div>
                  <span>{t("cert.issued")}</span>
                  <strong>
                    <CalendarDays size={15} />
                    {new Date(certificate.issued_at).toLocaleDateString(
                      language === "uz" ? "uz-UZ" : "ru-RU",
                    )}
                  </strong>
                </div>
              </div>

              <div className="certificate-id-box">
                <Award size={17} />
                <span>{t("cert.certificateId")}</span>
                <code>{certificate.id}</code>
              </div>

              <div className="verify-actions">
                <Link className="button button-ghost" href="/">
                  CyberSafe Uzbekistan
                </Link>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </section>
  );
}
