export interface APIResponse<T> {
  success: true;
  data: T;
  meta?: Record<string, unknown> | null;
}

export interface APIErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  email_verified_at?: string | null;
  created_at: string;
}

export interface Account {
  id: string;
  name: string;
  type: "individual" | "team" | string;
  owner_user_id: string;
  timezone: string;
  currency: string;
  created_at: string;
  role?: string | null;
}

export interface Membership {
  id: string;
  account_id: string;
  user_id: string;
  role: string;
  status: string;
  created_at: string;
  user_email: string;
  user_full_name: string;
}

export interface AuthSession {
  user: User;
  accounts: Account[];
  active_account_id: string | null;
  google_oauth_enabled: boolean;
}

