import { useState } from "react";
import { ShieldCheck, Sparkles, Terminal, Wallet } from "lucide-react";
import { AppLayout } from "@/layouts/AppLayout";
import { Alert, Badge, Button, Card } from "@/components/ui/primitives";
import { useAuth } from "@/contexts/AuthContext";
import { authApi } from "@/services/api";

export function DashboardPage() {
  const { user, activeAccount } = useAuth();
  const [resent, setResent] = useState(false);

  async function handleResend() {
    await authApi.resendVerification();
    setResent(true);
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              Espaço ativo: <span className="font-medium text-foreground">{activeAccount?.name}</span>{" "}
              ({activeAccount?.currency} · {activeAccount?.timezone})
            </p>
          </div>
          <Badge variant="default">Fase 1 — Fundação ativa</Badge>
        </div>

        {user && !user.email_verified_at && (
          <Alert variant="info" className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span>
              Seu e-mail (<strong>{user.email}</strong>) ainda não foi verificado.
            </span>
            <Button size="sm" variant="outline" onClick={() => void handleResend()} disabled={resent}>
              {resent ? "E-mail reenviado" : "Reenviar verificação"}
            </Button>
          </Alert>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="p-5 space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Tokens totais</p>
            <p className="text-2xl font-bold">—</p>
            <p className="text-xs text-muted-foreground">Sem dados coletados ainda</p>
          </Card>
          <Card className="p-5 space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Custo estimado</p>
            <p className="text-2xl font-bold">—</p>
            <p className="text-xs text-muted-foreground">Aguardando integração</p>
          </Card>
          <Card className="p-5 space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Provedores conectados</p>
            <p className="text-2xl font-bold">0</p>
            <p className="text-xs text-muted-foreground">Disponível na Fase 2</p>
          </Card>
          <Card className="p-5 space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Isolamento da conta</p>
            <p className="text-2xl font-bold text-emerald-400">Ativo</p>
            <p className="text-xs text-muted-foreground">Multi-tenant validado</p>
          </Card>
        </div>

        <Card className="p-6 space-y-4">
          <div className="flex items-center gap-2 text-base font-semibold">
            <Sparkles className="h-5 w-5 text-primary" />
            Fundação multi-tenant pronta para as integrações
          </div>
          <p className="text-sm text-muted-foreground">
            Esta é a entrega da <strong>Fase 1</strong>: autenticação por sessão segura, contas
            isoladas por usuário/workspace e proteção contra acesso entre contas. Na{" "}
            <strong>Fase 2</strong> serão adicionados o cofre de credenciais AES-256-GCM, o
            conector Google Gemini API e a ingestão instrumentada.
          </p>
          <div className="grid gap-3 pt-2 sm:grid-cols-3">
            <div className="rounded-lg border border-border bg-background/50 p-4 space-y-1">
              <ShieldCheck className="h-4 w-4 text-primary" />
              <p className="text-sm font-medium">Isolamento por conta</p>
              <p className="text-xs text-muted-foreground">
                Header X-Account-ID validado contra memberships + PostgreSQL RLS.
              </p>
            </div>
            <div className="rounded-lg border border-border bg-background/50 p-4 space-y-1">
              <Terminal className="h-4 w-4 text-primary" />
              <p className="text-sm font-medium">Métricas honestas</p>
              <p className="text-xs text-muted-foreground">
                Campos não coletados exibem ausência explícita, nunca zero artificial.
              </p>
            </div>
            <div className="rounded-lg border border-border bg-background/50 p-4 space-y-1">
              <Wallet className="h-4 w-4 text-primary" />
              <p className="text-sm font-medium">APIs vs. Assinaturas</p>
              <p className="text-xs text-muted-foreground">
                Consumo pago por uso separado de planos como Gemini App e Antigravity.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
}

