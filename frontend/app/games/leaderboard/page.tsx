"use client";

import { Trophy } from "lucide-react";
import { useEffect, useState } from "react";

import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { WebGameLeaderboardEntry } from "@/lib/webgame-types";

export default function GamesLeaderboardPage() {
  const { language } = useLanguage();
  const [rows, setRows] = useState<WebGameLeaderboardEntry[]>([]);

  useEffect(() => {
    api<WebGameLeaderboardEntry[]>("/webgame/leaderboard/")
      .then(setRows)
      .catch(() => setRows([]));
  }, []);

  return (
    <section className="page-section games-page">
      <div className="container narrow-container">
        <div className="section-heading compact">
          <span className="eyebrow">
            <Trophy size={16} />{" "}
            {language === "uz" ? "O‘yin reytingi" : "Рейтинг игры"}
          </span>
          <h1>CyberSafe Missions</h1>
          <p>
            {language === "uz"
              ? "Eng ko‘p ball to‘plagan foydalanuvchilar."
              : "Пользователи с лучшим суммарным результатом в 3D-миссиях."}
          </p>
        </div>

        <div className="game-leaderboard-table">
          {rows.map((row) => (
            <div key={row.rank}>
              <span>#{row.rank}</span>
              <strong>{row.user_name}</strong>
              <small>
                {row.total_score} ·{" "}
                {language === "uz" ? "missiyalar" : "миссий"}:{" "}
                {row.missions_completed}
              </small>
            </div>
          ))}
          {rows.length === 0 && (
            <div>
              <strong>{language === "uz" ? "Hali natijalar yo‘q" : "Пока нет результатов"}</strong>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
