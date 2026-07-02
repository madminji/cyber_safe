"use client";

import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import {
  Language,
  translate,
  TranslationKey,
} from "@/lib/translations";

const LanguageContext = createContext<{
  language: Language;
  setLanguage: (language: Language) => void;
  t: (
    key: TranslationKey,
    variables?: Record<string, string | number>,
  ) => string;
} | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>("ru");

  useEffect(() => {
    const saved = localStorage.getItem("cybersafe_language");
    if (saved === "ru" || saved === "uz") setLanguageState(saved);
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const setLanguage = (next: Language) => {
    setLanguageState(next);
    localStorage.setItem("cybersafe_language", next);
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t: (key, variables) => translate(language, key, variables),
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("LanguageProvider is missing");
  return context;
}
