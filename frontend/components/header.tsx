"use client";

import {
  ChevronDown,
  Gavel,
  LogIn,
  LogOut,
  Menu,
  UserRound,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Logo } from "@/components/logo";
import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";

const links = [
  { href: "/courses", label: "header.courses" },
  { href: "/analyzer", label: "header.analyzer" },
  { href: "/quiz", label: "header.quiz" },
  { href: "/simulator", label: "header.simulator" },
] as const;

const secondaryLinks = [
  { href: "/daily-quiz", label: "header.daily" },
  { href: "/leaderboard", label: "header.leaderboard" },
  { href: "/certificates", label: "header.certificates" },
  { href: "/numbers/report", label: "header.report" },
] as const;

export function Header() {
  const pathname = usePathname();
  const { user, logout, loading } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [open, setOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreActive = secondaryLinks.some((link) => pathname.startsWith(link.href));

  const closeNavigation = () => {
    setOpen(false);
    setMoreOpen(false);
  };

  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link href="/" aria-label="CyberSafe Uzbekistan">
          <Logo />
        </Link>
        <nav className={open ? "main-nav open" : "main-nav"}>
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={pathname.startsWith(link.href) ? "active" : ""}
              onClick={closeNavigation}
            >
              {t(link.label)}
            </Link>
          ))}
          <div className={moreOpen ? "nav-more open" : "nav-more"}>
            <button
              className={moreActive ? "active" : ""}
              onClick={() => setMoreOpen((value) => !value)}
              type="button"
            >
              {t("header.more")} <ChevronDown size={15} />
            </button>
            <div className="nav-more-menu">
              {secondaryLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={pathname.startsWith(link.href) ? "active" : ""}
                  onClick={closeNavigation}
                >
                  {t(link.label)}
                </Link>
              ))}
            </div>
          </div>
        </nav>
        <div className="header-actions">
          <div className="language-switch" aria-label={t("header.language")}>
            <button
              className={language === "ru" ? "active" : ""}
              onClick={() => setLanguage("ru")}
            >
              RU
            </button>
            <button
              className={language === "uz" ? "active" : ""}
              onClick={() => setLanguage("uz")}
            >
              UZ
            </button>
          </div>
          {!loading &&
            (user ? (
              <>
                {(user.role === "moderator" || user.role === "admin") && (
                  <Link
                    href="/moderation"
                    className="icon-link moderation-link"
                    title={t("header.moderationTitle")}
                  >
                    <Gavel size={18} />
                    <span>{t("header.moderation")}</span>
                  </Link>
                )}
                <Link
                  href="/account"
                  className="icon-link"
                  title={t("header.accountTitle")}
                >
                  <UserRound size={18} />
                  <span>{user.full_name?.split(" ")[0] || t("header.account")}</span>
                </Link>
                <button
                  className="icon-button"
                  onClick={logout}
                  title={t("header.logout")}
                >
                  <LogOut size={18} />
                </button>
              </>
            ) : (
              <Link className="button button-small button-dark" href="/login">
                <LogIn size={17} />
                {t("header.login")}
              </Link>
            ))}
          <button
            className="mobile-menu"
            onClick={() => setOpen((value) => !value)}
            aria-label={t("header.menu")}
          >
            {open ? <X /> : <Menu />}
          </button>
        </div>
      </div>
    </header>
  );
}
