import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { Alert, Button, Input, Label } from "@/components/ui/primitives";
import { ApiClientError, authApi } from "@/services/api";

export function ResetPasswordPage() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [newPassword, setNewPassword] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await authApi.resetPassword({ token, new_password: newPassword });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Erro ao redefinir senha.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout
      title="Definir nova senha"
      subtitle="Após redefinir, todas as sessões anteriores serão encerradas."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert variant="error">{error}</Alert>}
        {done && (
          <Alert variant="success">
            Senha atualizada com sucesso!{" "}
            <Link to="/login" className="underline">
              Entrar agora
            </Link>
            .
          </Alert>
        )}

        {!done && (
          <>
            <div className="space-y-1.5">
              <Label htmlFor="newPassword">Nova senha (mínimo 8 caracteres)</Label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            <Button type="submit" className="w-full" disabled={busy || !token}>
              {busy ? "Salvando..." : "Atualizar senha"}
            </Button>
          </>
        )}

        {!token && (
          <Alert variant="error">Token de redefinição ausente na URL.</Alert>
        )}
      </form>
    </AuthLayout>
  );
}

