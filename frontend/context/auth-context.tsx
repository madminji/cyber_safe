"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { api, clearTokens, hasToken, storeTokens } from "@/lib/api";
import { User } from "@/lib/types";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  requestOtp: (payload: {
    phone: string;
    full_name?: string;
    region?: string;
    language: "ru" | "uz";
  }) => Promise<{ challenge_id: string; development_otp?: string }>;
  verifyOtp: (payload: {
    phone: string;
    challenge_id: string;
    code: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  reloadUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const reloadUser = useCallback(async () => {
    if (!hasToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      setUser(await api<User>("/auth/me/", { auth: true }));
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reloadUser();
  }, [reloadUser]);

  const requestOtp: AuthContextValue["requestOtp"] = (payload) =>
    api("/auth/request-otp/", {
      method: "POST",
      body: JSON.stringify(payload),
    });

  const verifyOtp: AuthContextValue["verifyOtp"] = async (payload) => {
    const response = await api<{
      access: string;
      refresh: string;
      user: User;
    }>("/auth/verify-otp/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    storeTokens(response.access, response.refresh);
    setUser(response.user);
  };

  const logout = async () => {
    const refresh = localStorage.getItem("cybersafe_refresh");
    try {
      if (refresh) {
        await api("/auth/logout/", {
          method: "POST",
          auth: true,
          body: JSON.stringify({ refresh }),
        });
      }
    } finally {
      clearTokens();
      setUser(null);
    }
  };

  const value = useMemo(
    () => ({ user, loading, requestOtp, verifyOtp, logout, reloadUser }),
    [user, loading, reloadUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}

