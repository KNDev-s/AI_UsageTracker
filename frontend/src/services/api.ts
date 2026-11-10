import type {
  APIErrorResponse,
  APIResponse,
  Account,
  AuthSession,
  Membership,
} from "@/types/api";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"
).replace(/\/$/, "");

export class ApiClientError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function readCookie(name: string): string | null {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = document.cookie.match(new RegExp(`(?:^|; )${escaped}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

let activeAccountIdRef: string | null = null;

export function setApiActiveAccountId(accountId: string | null): void {
  activeAccountIdRef = accountId;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method || "GET").toUpperCase();
  const headers = new Headers(init.headers);

  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  if (activeAccountIdRef && !headers.has("X-Account-ID")) {
    headers.set("X-Account-ID", activeAccountIdRef);
  }
  if (["POST", "PATCH", "PUT", "DELETE"].includes(method)) {
    const csrfToken = readCookie("ai_tracker_csrf");
    if (csrfToken) {
      headers.set("X-CSRF-Token", csrfToken);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    method,
    headers,
    credentials: "include",
  });

  const payload = (await response.json().catch(() => null)) as
    | APIResponse<T>
    | APIErrorResponse
    | null;

  if (!response.ok || !payload || !payload.success) {
    const err = payload && !payload.success ? payload.error : null;
    throw new ApiClientError(
      response.status,
      err?.code || "request_failed",
      err?.message || "Erro ao comunicar com o servidor."
    );
  }

  return payload.data;
}

export const authApi = {
  me: () => request<AuthSession>("/auth/me"),
  login: (body: { email: string; password: string }) =>
    request<AuthSession>("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  register: (body: { email: string; password: string; full_name: string }) =>
    request<AuthSession>("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  logout: () => request<{ logged_out: boolean }>("/auth/logout", { method: "POST" }),
  verifyEmail: (token: string) =>
    request<{ verified: boolean }>("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),
  resendVerification: () =>
    request<{ sent: boolean }>("/auth/resend-verification", { method: "POST" }),
  forgotPassword: (email: string) =>
    request<{ accepted: boolean }>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),
  resetPassword: (body: { token: string; new_password: string }) =>
    request<{ reset: boolean }>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  googleLoginUrl: () => `${API_BASE_URL}/auth/google`,
};

export const accountsApi = {
  list: () => request<Account[]>("/accounts"),
  create: (body: { name: string; type?: "individual" | "team"; currency?: string }) =>
    request<Account>("/accounts", { method: "POST", body: JSON.stringify(body) }),
  update: (accountId: string, body: { name?: string; timezone?: string; currency?: string }) =>
    request<Account>(`/accounts/${accountId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  remove: (accountId: string) =>
    request<{ deleted: boolean }>(`/accounts/${accountId}`, { method: "DELETE" }),
  exportData: (accountId: string) =>
    request<Record<string, unknown>>(`/accounts/${accountId}/export`, { method: "POST" }),
  members: (accountId: string) => request<Membership[]>(`/accounts/${accountId}/members`),
};

