import { useState } from "react";
import { Link } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { Alert, Button, Input, Label } from "@/components/ui/primitives";
import { ApiClientError, authApi } from "@/services/api";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await authApi.forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Erro ao solicitar recuperação.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout
      title="Recuperar senha"
      subtitle="Enviaremos um link de redefinição caso o e-mail esteja cadastrado."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert variant="error">{error}</Alert>}
        {sent && (
          <Alert variant="success">
            Se o e-mail existir em nossa base, você receberá as instruções em instantes.
          </Alert>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="email">E-mail</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <Button type="submit" className="w-full" disabled={busy}>
          {busy ? "Enviando..." : "Enviar instruções"}
        </Button>

        <p className="pt-2 text-center text-sm text-muted-foreground">
          <Link to="/login" className="text-primary hover:underline">
            Voltar para o login
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

