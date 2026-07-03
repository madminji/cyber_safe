"use client";

import { Medal, Star, Trophy } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { LeaderboardEntry } from "@/lib/types";

const copy = {
  ru: {
    eyebrow: "Рейтинг платформы",
    title: "Лидеры CyberSafe",
    lead: "Общий рейтинг строится по баллам за тесты, ежедневные задания, курсы и симуляции.",
    points: "баллов",
    you: "это вы",
    empty: "Пока нет участников рейтинга",
    account: "Вернуться в кабинет",
  },
  uz: {
    eyebrow: "Platforma reytingi",
    title: "CyberSafe yetakchilari",
    lead: "Umumiy reyting testlar, kunlik topshiriqlar, kurslar va simulyatsiyalar uchun berilgan ballar asosida tuziladi.",
    points: "ball",
    you: "bu siz",
    empty: "Hozircha reytingda ishtirokchilar yo‘q",
    account: "Kabinetga qaytish",
  },
} as const;

export default function LeaderboardPage() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const text = copy[language];
  const [rows, setRows] = useState<LeaderboardEntry[]>([]);
  const [busy, setBusy] = useState(true);

  useEffect(() => {
    api<LeaderboardEntry[]>("/auth/leaderboard/", { auth: Boolean(user) })
      .then(setRows)
      .catch(() => setRows([]))
      .finally(() => setBusy(false));
  }, [user]);

  return (
    <section className="page-section leaderboard-page">
      <div className="container narrow-container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <Trophy size={16} /> {text.eyebrow}
          </span>
          <h1>{text.title}</h1>
          <p>{text.lead}</p>
        </div>

        <div className="platform-leaderboard">
          {busy ? (
            <div className="loading-card">
              <span className="loader" />
            </div>
          ) : rows.length ? (
            rows.map((row) => (
              <article
                className={row.is_current_user ? "current-user" : ""}
                key={row.rank}
              >
                <span className="leaderboard-rank">
                  {row.rank <= 3 ? <Medal size={18} /> : `#${row.rank}`}
                </span>
                <div>
                  <strong>{row.user_name}</strong>
                  {row.is_current_user && <small>{text.you}</small>}
                </div>
                <p>
                  <Star size={15} /> {row.points} {text.points}
                </p>
              </article>
            ))
          ) : (
            <div className="panel-empty">
              <Trophy />
              <p>{text.empty}</p>
            </div>
          )}
        </div>

        {user && (
          <div className="result-actions">
            <Link className="button button-ghost" href="/account">
              {text.account}
            </Link>
          </div>
        )}
      </div>
    </section>
  );
}
