import { useState, type ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Activity,
  BarChart3,
  Cpu,
  CreditCard,
  History,
  LayoutDashboard,
  Lightbulb,
  LogOut,
  Menu,
  Plug,
  Settings,
  X,
} from "lucide-react";
import { AccountSwitcher } from "@/components/AccountSwitcher";
import { Badge, Button } from "@/components/ui/primitives";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, enabled: true },
  { to: "/analytics", label: "Analytics", icon: BarChart3, enabled: false },
  { to: "/integrations", label: "Integrações", icon: Plug, enabled: false },
  { to: "/models", label: "Modelos", icon: Cpu, enabled: false },
  { to: "/history", label: "Histórico", icon: History, enabled: false },
  { to: "/costs", label: "Custos e assinaturas", icon: CreditCard, enabled: false },
  { to: "/insights", label: "Insights", icon: Lightbulb, enabled: false },
  { to: "/settings", label: "Configurações", icon: Settings, enabled: true },
];

export function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebarContent = (
    <div className="flex h-full flex-col justify-between p-4">
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/15 text-primary">
              <Activity className="h-5 w-5" />
            </div>
            <span className="font-semibold tracking-tight">AI Usage Tracker</span>
          </Link>
          <button
            type="button"
            className="rounded-md p-1 text-muted-foreground lg:hidden"
            onClick={() => setMobileOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <AccountSwitcher />

        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.to;
            if (!item.enabled) {
              return (
                <div
                  key={item.to}
                  className="flex items-center justify-between rounded-lg px-3 py-2 text-sm text-muted-foreground/55"
                >
                  <span className="flex items-center gap-2.5">
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </span>
                  <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                    Fase 2+
                  </Badge>
                </div>
              );
            }
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="space-y-3 border-t border-border pt-4">
        <div className="text-xs">
          <p className="truncate font-medium text-foreground">{user?.full_name}</p>
          <p className="truncate text-muted-foreground">{user?.email}</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="w-full justify-start"
          onClick={() => void logout()}
        >
          <LogOut className="h-4 w-4" /> Sair
        </Button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background text-foreground lg:grid lg:grid-cols-[270px_1fr]">
      <aside className="hidden border-r border-border bg-card lg:block">{sidebarContent}</aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div className="w-72 border-r border-border bg-card">{sidebarContent}</div>
          <div
            className="flex-1 bg-black/60"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />
        </div>
      )}

      <div className="flex min-w-0 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-border bg-card/70 px-4 lg:hidden">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="rounded-md p-2 text-muted-foreground hover:bg-secondary"
            aria-label="Abrir menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <span className="text-sm font-semibold">AI Usage Tracker</span>
          <div className="w-9" />
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}

