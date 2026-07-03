"use client";

import { Trophy } from "lucide-react";
import { useEffect, useState } from "react";

import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { WebGameLeaderboardEntry } from "@/lib/webgame-types";

const leaderboardCopy = {
  ru: {
    eyebrow: "\u0420\u0435\u0439\u0442\u0438\u043d\u0433 \u0438\u0433\u0440\u044b",
    lead: "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 \u0441 \u043b\u0443\u0447\u0448\u0438\u043c \u0441\u0443\u043c\u043c\u0430\u0440\u043d\u044b\u043c \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u043e\u043c \u0432 3D-\u043c\u0438\u0441\u0441\u0438\u044f\u0445.",
    missions: "\u043c\u0438\u0441\u0441\u0438\u0439",
    empty: "\u041f\u043e\u043a\u0430 \u043d\u0435\u0442 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u043e\u0432",
  },
  uz: {
    eyebrow: "O\u2018yin reytingi",
    lead: "Eng ko\u2018p ball to\u2018plagan foydalanuvchilar.",
    missions: "missiyalar",
    empty: "Hali natijalar yo\u2018q",
  },
} as const;

export default function GamesLeaderboardPage() {
  const { language } = useLanguage();
  const copy = leaderboardCopy[language];
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
            <Trophy size={16} /> {copy.eyebrow}
          </span>
          <h1>CyberSafe Missions</h1>
          <p>{copy.lead}</p>
        </div>

        <div className="game-leaderboard-table">
          {rows.map((row) => (
            <div key={row.rank}>
              <span>#{row.rank}</span>
              <strong>{row.user_name}</strong>
              <small>
                {row.total_score} \u00b7 {copy.missions}:{" "}
                {row.missions_completed}
              </small>
            </div>
          ))}
          {rows.length === 0 && (
            <div>
              <strong>{copy.empty}</strong>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
