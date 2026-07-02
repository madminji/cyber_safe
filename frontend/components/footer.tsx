"use client";

import Link from "next/link";

import { Logo } from "@/components/logo";
import { useLanguage } from "@/context/language-context";

export function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <Logo />
          <p>{t("footer.description")}</p>
        </div>
        <div>
          <strong>{t("footer.tools")}</strong>
          <Link href="/quiz">{t("footer.quiz")}</Link>
          <Link href="/courses">{t("footer.courses")}</Link>
          <Link href="/simulator">{t("footer.simulator")}</Link>
          <Link href="/analyzer">{t("footer.analyzer")}</Link>
          <Link href="/analyzer#phone">{t("footer.numbers")}</Link>
          <Link href="/numbers/report">{t("footer.report")}</Link>
          <Link href="/certificates">{t("footer.certificates")}</Link>
        </div>
        <div>
          <strong>{t("footer.important")}</strong>
          <p>{t("footer.warning")}</p>
          <span className="footer-note">© 2026 CyberSafe Uzbekistan</span>
        </div>
      </div>
    </footer>
  );
}
