const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

type RequestOptions = RequestInit & { auth?: boolean };
type ClientLanguage = "ru" | "uz";

function getStoredToken(name: "access" | "refresh") {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(`cybersafe_${name}`);
}

export function hasToken() {
  return Boolean(getStoredToken("access"));
}

export function storeTokens(access: string, refresh: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem("cybersafe_access", access);
  localStorage.setItem("cybersafe_refresh", refresh);
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("cybersafe_access");
  localStorage.removeItem("cybersafe_refresh");
}

function getStoredLanguage(): ClientLanguage {
  if (typeof window === "undefined") return "ru";
  return localStorage.getItem("cybersafe_language") === "uz" ? "uz" : "ru";
}

function fallbackError(key: "server" | "connection" | "request", status?: number) {
  const language = getStoredLanguage();
  if (language === "uz") {
    if (key === "server") {
      return `Server ${status} xatosini qaytardi. Qayta urinib ko\u2018ring.`;
    }
    if (key === "connection") return "Server bilan bog\u2018lanib bo\u2018lmadi";
    return "So\u2018rovni bajarib bo\u2018lmadi";
  }
  if (key === "server") {
    return `\u0421\u0435\u0440\u0432\u0435\u0440 \u0432\u0435\u0440\u043d\u0443\u043b \u043e\u0448\u0438\u0431\u043a\u0443 ${status}. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0435\u0449\u0451 \u0440\u0430\u0437.`;
  }
  if (key === "connection") {
    return "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0441\u0432\u044f\u0437\u0430\u0442\u044c\u0441\u044f \u0441 \u0441\u0435\u0440\u0432\u0435\u0440\u043e\u043c";
  }
  return "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0432\u044b\u043f\u043e\u043b\u043d\u0438\u0442\u044c \u0437\u0430\u043f\u0440\u043e\u0441";
}

function extractError(payload: unknown, status?: number): string {
  if (!payload || typeof payload !== "object") {
    return status ? fallbackError("server", status) : fallbackError("connection");
  }
  const data = payload as Record<string, unknown>;
  const details =
    (data.error as Record<string, unknown> | undefined)?.details || data;
  if (typeof details === "string") return details;
  if (details && typeof details === "object") {
    const value = Object.values(details)[0];
    if (Array.isArray(value)) return String(value[0]);
    if (typeof value === "string") return value;
  }
  return fallbackError("request");
}

async function refreshAccessToken() {
  const refresh = getStoredToken("refresh");
  if (!refresh) return null;
  const response = await fetch(`${API_URL}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return null;
  const data = await response.json();
  localStorage.setItem("cybersafe_access", data.access);
  if (data.refresh) localStorage.setItem("cybersafe_refresh", data.refresh);
  return data.access as string;
}

export async function api<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }
  if (options.auth) {
    const access = getStoredToken("access");
    if (access) headers.set("Authorization", `Bearer ${access}`);
  }

  let response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (response.status === 401 && options.auth) {
    const access = await refreshAccessToken();
    if (access) {
      headers.set("Authorization", `Bearer ${access}`);
      response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers,
        cache: "no-store",
      });
    }
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : null;
  if (!response.ok) throw new Error(extractError(payload, response.status));
  return payload as T;
}
