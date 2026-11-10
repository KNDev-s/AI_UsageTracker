import { useEffect, useState } from "react";
import { Download } from "lucide-react";
import { AppLayout } from "@/layouts/AppLayout";
import { Alert, Badge, Button, Card, Input, Label } from "@/components/ui/primitives";
import { useAuth } from "@/contexts/AuthContext";
import { accountsApi, ApiClientError } from "@/services/api";
import type { Membership } from "@/types/api";

export function AccountSettingsPage() {
  const { activeAccount, refreshSession } = useAuth();
  const [name, setName] = useState(activeAccount?.name || "");
  const [currency, setCurrency] = useState(activeAccount?.currency || "BRL");
  const [timezone, setTimezone] = useState(activeAccount?.timezone || "America/Sao_Paulo");
  const [members, setMembers] = useState<Membership[]>([]);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeAccount) return;
    setName(activeAccount.name);
    setCurrency(activeAccount.currency);
    setTimezone(activeAccount.timezone);
    accountsApi
      .members(activeAccount.id)
      .then(setMembers)
      .catch(() => setMembers([]));
  }, [activeAccount]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!activeAccount) return;
    setError(null);
    setSaved(false);
    try {
      await accountsApi.update(activeAccount.id, { name, currency, timezone });
      await refreshSession(activeAccount.id);
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Erro ao salvar.");
    }
  }

  async function handleExport() {
    if (!activeAccount) return;
    const data = await accountsApi.exportData(activeAccount.id);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ai-usage-tracker-${activeAccount.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <AppLayout>
      <div className="max-w-3xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Configurações da conta</h1>
          <p className="text-sm text-muted-foreground">
            Preferências do espaço ativo, membros e portabilidade de dados (LGPD).
          </p>
        </div>

        <Card className="p-6">
          <form onSubmit={handleSave} className="space-y-4">
            {error && <Alert variant="error">{error}</Alert>}
            {saved && <Alert variant="success">Configurações atualizadas com sucesso.</Alert>}

            <div className="space-y-1.5">
              <Label htmlFor="accName">Nome da conta</Label>
              <Input id="accName" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="currency">Moeda padrão</Label>
                <Input
                  id="currency"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value.toUpperCase())}
                  maxLength={8}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="timezone">Fuso horário</Label>
                <Input
                  id="timezone"
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  required
                />
              </div>
            </div>

            <Button type="submit">Salvar alterações</Button>
          </form>
        </Card>

        <Card className="p-6 space-y-3">
          <h2 className="text-base font-semibold">Membros do espaço</h2>
          <div className="divide-y divide-border">
            {members.map((m) => (
              <div key={m.id} className="flex items-center justify-between py-2.5 text-sm">
                <div>
                  <p className="font-medium">{m.user_full_name}</p>
                  <p className="text-xs text-muted-foreground">{m.user_email}</p>
                </div>
                <Badge>{m.role}</Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card className="flex flex-col gap-3 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-base font-semibold">Exportação de dados (LGPD)</h2>
            <p className="text-xs text-muted-foreground">
              Baixe um snapshot JSON com os dados cadastrais deste espaço.
            </p>
          </div>
          <Button variant="outline" onClick={() => void handleExport()}>
            <Download className="h-4 w-4" /> Exportar JSON
          </Button>
        </Card>
      </div>
    </AppLayout>
  );
}

