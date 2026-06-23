"use client";

import {
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
  { href: "/quiz", ru: "Тест", uz: "Test" },
  { href: "/courses", ru: "Курсы", uz: "Kurslar" },
  { href: "/simulator", ru: "Симулятор", uz: "Simulyator" },
  { href: "/analyzer", ru: "Анализатор", uz: "Tahlil" },
  { href: "/numbers", ru: "Проверить номер", uz: "Raqamni tekshirish" },
  { href: "/certificates", ru: "Сертификаты", uz: "Sertifikatlar" },
];

export function Header() {
  const pathname = usePathname();
  const { user, logout, loading } = useAuth();
  const { language, setLanguage } = useLanguage();
  const [open, setOpen] = useState(false);

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
              onClick={() => setOpen(false)}
            >
              {link[language]}
            </Link>
          ))}
        </nav>
        <div className="header-actions">
          <div className="language-switch" aria-label="Выбор языка">
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
                    title="Панель модератора"
                  >
                    <Gavel size={18} />
                    <span>Модерация</span>
                  </Link>
                )}
                <Link href="/account" className="icon-link" title="Личный кабинет">
                  <UserRound size={18} />
                  <span>{user.full_name?.split(" ")[0] || "Кабинет"}</span>
                </Link>
                <button className="icon-button" onClick={logout} title="Выйти">
                  <LogOut size={18} />
                </button>
              </>
            ) : (
              <Link className="button button-small button-dark" href="/login">
                <LogIn size={17} />
                Войти
              </Link>
            ))}
          <button
            className="mobile-menu"
            onClick={() => setOpen((value) => !value)}
            aria-label="Открыть меню"
          >
            {open ? <X /> : <Menu />}
          </button>
        </div>
      </div>
    </header>
  );
}
