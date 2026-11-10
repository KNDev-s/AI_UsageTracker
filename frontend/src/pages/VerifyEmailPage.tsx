import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { Alert, Button } from "@/components/ui/primitives";
import { ApiClientError, authApi } from "@/services/api";

export function VerifyEmailPage() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Validando token de verificação...");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Token de verificação não encontrado.");
      return;
    }
    authApi
      .verifyEmail(token)
      .then(() => {
        setStatus("success");
        setMessage("E-mail verificado com sucesso!");
      })
      .catch((err) => {
        setStatus("error");
        setMessage(
          err instanceof ApiClientError ? err.message : "Não foi possível verificar o e-mail."
        );
      });
  }, [token]);

  return (
    <AuthLayout title="Verificação de e-mail" subtitle="Confirmação do endereço cadastrado.">
      <div className="space-y-4">
        <Alert variant={status === "error" ? "error" : status === "success" ? "success" : "info"}>
          {message}
        </Alert>
        <Link to="/dashboard" className="block">
          <Button className="w-full">Ir para o dashboard</Button>
        </Link>
      </div>
    </AuthLayout>
  );
}

