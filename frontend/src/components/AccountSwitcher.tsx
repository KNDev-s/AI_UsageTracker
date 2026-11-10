import { useState } from "react";
import { Building2, Plus } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { accountsApi } from "@/services/api";
import { Button, Input } from "@/components/ui/primitives";

export function AccountSwitcher() {
  const { accounts, activeAccount, switchAccount, refreshSession } = useAuth();
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    setBusy(true);
    try {
      const created = await accountsApi.create({ name: newName.trim(), type: "individual" });
      setNewName("");
      setCreating(false);
      await refreshSession(created.id);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2 rounded-lg border border-border bg-background/60 p-3">
      <div className="flex items-center justify-between text-xs font-medium text-muted-foreground">
        <span className="flex items-center gap-1.5">
          <Building2 className="h-3.5 w-3.5" /> Conta ativa
        </span>
        <button
          type="button"
          onClick={() => setCreating((v) => !v)}
          className="inline-flex items-center gap-1 text-primary hover:underline"
        >
          <Plus className="h-3.5 w-3.5" /> Nova
        </button>
      </div>

      <select
        aria-label="Selecionar conta"
        value={activeAccount?.id || ""}
        onChange={(e) => void switchAccount(e.target.value)}
        className="w-full rounded-md border border-input bg-card px-2.5 py-1.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      >
        {accounts.map((acc) => (
          <option key={acc.id} value={acc.id}>
            {acc.name} ({acc.currency})
          </option>
        ))}
      </select>

      {creating && (
        <form onSubmit={handleCreate} className="space-y-2 pt-1">
          <Input
            placeholder="Nome do espaço"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            required
          />
          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={busy} className="flex-1">
              Criar
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => setCreating(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}

