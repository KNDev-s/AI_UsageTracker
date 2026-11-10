import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { Alert, Button, Input, Label } from "@/components/ui/primitives";
import { useAuth } from "@/contexts/AuthContext";
import { ApiClientError, authApi } from "@/services/api";

export function RegisterPage() {
  const navigate = useNavigate();
  const { setSessionData, googleOAuthEnabled } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const session = await authApi.register({ full_name: fullName, email, password });
      setSessionData(session);
      navigate("/onboarding", { replace: true });
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Erro ao criar conta.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout
      title="Criar sua conta"
      subtitle="Um espaço individual isolado será criado automaticamente."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert variant="error">{error}</Alert>}

        <div className="space-y-1.5">
          <Label htmlFor="fullName">Nome completo</Label>
          <Input
            id="fullName"
            type="text"
            autoComplete="name"
            placeholder="Maria Oliveira"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            minLength={2}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email">E-mail</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="voce@empresa.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password">Senha (mínimo 8 caracteres)</Label>
          <Input
            id="password"
            type="password"
            autoComplete="new-password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </div>

        <Button type="submit" className="w-full" disabled={busy}>
          {busy ? "Criando conta..." : "Criar conta"}
        </Button>

        {googleOAuthEnabled && (
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={() => {
              window.location.href = authApi.googleLoginUrl();
            }}
          >
            Cadastrar com Google
          </Button>
        )}

        <p className="pt-2 text-center text-sm text-muted-foreground">
          Já tem conta?{" "}
          <Link to="/login" className="font-medium text-primary hover:underline">
            Entrar
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

