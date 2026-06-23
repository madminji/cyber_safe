import Link from "next/link";

import { Logo } from "@/components/logo";

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <Logo />
          <p>
            Национальная образовательная платформа цифровой безопасности
            граждан Узбекистана.
          </p>
        </div>
        <div>
          <strong>Инструменты</strong>
          <Link href="/quiz">Тест знаний</Link>
          <Link href="/courses">Обучающие курсы</Link>
          <Link href="/simulator">Симулятор мошенничества</Link>
          <Link href="/analyzer">Анализатор SMS и ссылок</Link>
          <Link href="/numbers">Проверка номера</Link>
          <Link href="/numbers/report">Сообщить о мошенничестве</Link>
          <Link href="/certificates">Сертификаты</Link>
        </div>
        <div>
          <strong>Важно</strong>
          <p>При финансовом инциденте немедленно свяжитесь со своим банком.</p>
          <span className="footer-note">© 2026 CyberSafe Uzbekistan</span>
        </div>
      </div>
    </footer>
  );
}
