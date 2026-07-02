"use client";

import {
  ArrowRight,
  BadgeCheck,
  BookOpenCheck,
  CheckCircle2,
  MessageSquareWarning,
  PhoneCall,
  SearchCheck,
  GraduationCap,
  BrainCircuit,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import Link from "next/link";

import { useLanguage } from "@/context/language-context";

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <>
      <section className="hero">
        <div className="hero-orb orb-one" />
        <div className="hero-orb orb-two" />
        <div className="container hero-grid">
          <div className="hero-copy">
            <span className="eyebrow">
              <Sparkles size={15} />
              {t("home.eyebrow")}
            </span>
            <h1>
              {t("home.titleBefore")} <em>{t("home.titleAccent")}</em>
            </h1>
            <p>
              {t("home.lead")}
            </p>
            <div className="hero-actions">
              <Link className="button button-primary" href="/quiz">
                {t("home.takeQuiz")}
                <ArrowRight size={18} />
              </Link>
              <Link className="button button-ghost" href="/analyzer#phone">
                {t("home.checkNumber")}
              </Link>
            </div>
            <div className="trust-row">
              <span>
                <CheckCircle2 size={17} /> {t("home.free")}
              </span>
              <span>
                <CheckCircle2 size={17} /> {t("home.safe")}
              </span>
              <span>
                <CheckCircle2 size={17} /> RU / UZ
              </span>
            </div>
          </div>
          <div className="hero-visual">
            <div className="shield-stage">
              <div className="shield-rings" />
              <div className="hero-shield">
                <ShieldAlert size={76} strokeWidth={1.45} />
                <span>CYBER</span>
                <strong>SAFE</strong>
              </div>
              <div className="floating-card card-a">
                <BadgeCheck size={22} />
                <span>
                  {t("home.certificate")}
                  <strong>{t("home.confirmed")}</strong>
                </span>
              </div>
              <div className="floating-card card-b">
                <PhoneCall size={22} />
                <span>
                  {t("home.number")}
                  <strong>{t("home.checked")}</strong>
                </span>
              </div>
              <div className="floating-card card-c">
                <BookOpenCheck size={22} />
                <span>
                  {t("home.level")}
                  <strong>{t("home.expert")}</strong>
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-heading">
            <span className="eyebrow">{t("home.shield")}</span>
            <h2>{t("home.toolsTitle")}</h2>
            <p>{t("home.toolsLead")}</p>
          </div>
          <div className="feature-grid">
            <Link href="/quiz" className="feature-card feature-blue">
              <span className="feature-icon">
                <BookOpenCheck />
              </span>
              <span className="feature-number">01</span>
              <h3>{t("home.featureQuizTitle")}</h3>
              <p>{t("home.featureQuizText")}</p>
              <span className="text-link">
                {t("home.startQuiz")} <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/analyzer#phone" className="feature-card feature-amber">
              <span className="feature-icon">
                <PhoneCall />
              </span>
              <span className="feature-number">02</span>
              <h3>{t("home.featureNumberTitle")}</h3>
              <p>{t("home.featureNumberText")}</p>
              <span className="text-link">
                {t("home.check")} <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/analyzer" className="feature-card feature-green">
              <span className="feature-icon">
                <SearchCheck />
              </span>
              <span className="feature-number">03</span>
              <h3>{t("home.featureAnalyzerTitle")}</h3>
              <p>{t("home.featureAnalyzerText")}</p>
              <span className="text-link">
                {t("home.openAnalyzer")} <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/courses" className="feature-card feature-cyan">
              <span className="feature-icon">
                <GraduationCap />
              </span>
              <span className="feature-number">04</span>
              <h3>{t("home.featureCoursesTitle")}</h3>
              <p>{t("home.featureCoursesText")}</p>
              <span className="text-link">
                {t("home.openCourses")} <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/simulator" className="feature-card feature-red">
              <span className="feature-icon">
                <BrainCircuit />
              </span>
              <span className="feature-number">05</span>
              <h3>{t("home.featureSimulatorTitle")}</h3>
              <p>{t("home.featureSimulatorText")}</p>
              <span className="text-link">
                {t("home.startSimulation")} <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/certificates" className="feature-card feature-violet">
              <span className="feature-icon">
                <BadgeCheck />
              </span>
              <span className="feature-number">06</span>
              <h3>{t("home.featureCertificateTitle")}</h3>
              <p>{t("home.featureCertificateText")}</p>
              <span className="text-link">
                {t("home.myCertificates")} <ArrowRight size={17} />
              </span>
            </Link>
          </div>
        </div>
      </section>

      <section className="danger-section">
        <div className="container danger-grid">
          <div>
            <span className="eyebrow eyebrow-light">
              <MessageSquareWarning size={15} /> {t("home.remember")}
            </span>
            <h2>{t("home.dangerTitle")}</h2>
          </div>
          <div className="danger-list">
            <p>{t("home.ruleCode")}</p>
            <p>{t("home.ruleApk")}</p>
            <p>{t("home.ruleAccount")}</p>
            <p>{t("home.ruleBank")}</p>
          </div>
        </div>
      </section>
    </>
  );
}
