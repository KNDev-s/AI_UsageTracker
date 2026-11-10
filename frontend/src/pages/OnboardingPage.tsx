import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle2, Sparkles } from "lucide-react";
import { AppLayout } from "@/layouts/AppLayout";
import { Badge, Button, Card } from "@/components/ui/primitives";
import { useAuth } from "@/contexts/AuthContext";

const PROVIDERS = [
  { id: "gemini_api", name: "Google Gemini API", desc: "Tokens e chamadas instrumentadas (Fase 2)" },
  { id: "antigravity", name: "Google Antigravity", desc: "Cotas e snapshots disponíveis (Fase 4)" },
  { id: "gemini_app", name: "Google Gemini App", desc: "Plano, mensalidade e limites (Fase 4)" },
];

export function OnboardingPage() {
  const navigate = useNavigate();
  const { activeAccount } = useAuth();
  const [selected, setSelected] = useState<string[]>(["gemini_api"]);

  function toggleProvider(id: string) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <Badge variant="default">Assistente inicial</Badge>
            <h1 className="mt-2 text-2xl font-bold">Bem-vindo ao AI Usage Tracker</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Seu espaço isolado <strong>{activeAccount?.name}</strong> já está pronto. Selecione
              as ferramentas que pretende acompanhar — você pode pular esta etapa quando quiser.
            </p>
          </div>
          <Button variant="ghost" onClick={() => navigate("/dashboard")}>
            Pular onboarding
          </Button>
        </div>

        <Card className="p-6 space-y-4">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Sparkles className="h-4 w-4 text-primary" />
            Ferramentas de IA prioritárias
          </div>

          <div className="space-y-2.5">
            {PROVIDERS.map((p) => {
              const checked = selected.includes(p.id);
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => toggleProvider(p.id)}
                  className={`flex w-full items-center justify-between rounded-lg border p-4 text-left transition-colors ${
                    checked
                      ? "border-primary bg-primary/10"
                      : "border-border bg-background/50 hover:bg-secondary/40"
                  }`}
                >
                  <div>
                    <p className="font-medium text-foreground">{p.name}</p>
                    <p className="text-xs text-muted-foreground">{p.desc}</p>
                  </div>
                  <CheckCircle2
                    className={`h-5 w-5 ${checked ? "text-primary" : "text-muted-foreground/30"}`}
                  />
                </button>
              );
            })}
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <Button variant="outline" onClick={() => navigate("/dashboard")}>
              Pular por enquanto
            </Button>
            <Button onClick={() => navigate("/dashboard")}>Ir para o dashboard</Button>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
}

