const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

type RequestOptions = RequestInit & { auth?: boolean };

function getStoredToken(name: "access" | "refresh") {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(`cybersafe_${name}`);
}

function extractError(payload: unknown, status?: number): string {
  if (!payload || typeof payload !== "object") {
    return status
      ? `Сервер вернул ошибку ${status}. Попробуйте ещё раз.`
      : "Не удалось связаться с сервером";
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
  return "Не удалось выполнить запрос";
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
  if (options.body && !headers.has("Content-Type")) {
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

export function storeTokens(access: string, refresh: string) {
  localStorage.setItem("cybersafe_access", access);
  localStorage.setItem("cybersafe_refresh", refresh);
}

export function clearTokens() {
  localStorage.removeItem("cybersafe_access");
  localStorage.removeItem("cybersafe_refresh");
}

export function hasToken() {
  return Boolean(getStoredToken("access"));
}

export { API_URL };
