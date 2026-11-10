import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { authApi, setApiActiveAccountId } from "@/services/api";
import type { Account, AuthSession, User } from "@/types/api";

interface AuthContextValue {
  loading: boolean;
  user: User | null;
  accounts: Account[];
  activeAccount: Account | null;
  googleOAuthEnabled: boolean;
  refreshSession: (accountIdOverride?: string | null) => Promise<void>;
  switchAccount: (accountId: string) => Promise<void>;
  setSessionData: (session: AuthSession) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<AuthSession | null>(null);

  const applySession = useCallback((next: AuthSession | null) => {
    setSession(next);
    setApiActiveAccountId(next?.active_account_id ?? null);
  }, []);

  const refreshSession = useCallback(
    async (accountIdOverride?: string | null) => {
      if (accountIdOverride !== undefined) {
        setApiActiveAccountId(accountIdOverride);
      }
      try {
        const data = await authApi.me();
        applySession(data);
      } catch {
        applySession(null);
      } finally {
        setLoading(false);
      }
    },
    [applySession]
  );

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  const switchAccount = useCallback(
    async (accountId: string) => {
      await refreshSession(accountId);
    },
    [refreshSession]
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      applySession(null);
    }
  }, [applySession]);

  const activeAccount =
    session?.accounts.find((acc) => acc.id === session.active_account_id) ||
    session?.accounts[0] ||
    null;

  return (
    <AuthContext.Provider
      value={{
        loading,
        user: session?.user ?? null,
        accounts: session?.accounts ?? [],
        activeAccount,
        googleOAuthEnabled: session?.google_oauth_enabled ?? false,
        refreshSession,
        switchAccount,
        setSessionData: applySession,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser utilizado dentro de AuthProvider.");
  }
  return ctx;
}

