"use client";

import { ReactNode } from "react";

import { AuthProvider } from "@/context/auth-context";
import { LanguageProvider } from "@/context/language-context";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <LanguageProvider>
      <AuthProvider>{children}</AuthProvider>
    </LanguageProvider>
  );
}

