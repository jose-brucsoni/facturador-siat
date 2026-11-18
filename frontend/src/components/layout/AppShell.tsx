import {
  Building2,
  FileText,
  LayoutDashboard,
  LogOut,
  Package,
  Receipt,
  Settings,
  Users,
} from "lucide-react"
import { NavLink, Outlet } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useAuth } from "@/lib/auth"
import { cn } from "@/lib/utils"

const nav = [
  { to: "/", label: "Inicio", icon: LayoutDashboard, end: true },
  { to: "/emitir", label: "Emitir", icon: Receipt },
  { to: "/facturas", label: "Facturas", icon: FileText },
  { to: "/clientes", label: "Clientes", icon: Users },
  { to: "/productos", label: "Productos", icon: Package },
  { to: "/config", label: "Config SIAT", icon: Settings },
]

export function AppShell() {
  const { user, logout } = useAuth()

  return (
    <div className="mx-auto flex min-h-screen max-w-7xl gap-0 md:gap-6 md:p-6">
      <aside className="hidden w-64 shrink-0 flex-col rounded-2xl border bg-card/90 p-4 shadow-sm backdrop-blur md:flex">
        <div className="mb-6 flex items-start gap-3 px-2">
          <div className="mt-0.5 rounded-lg bg-primary/10 p-2 text-primary">
            <Building2 className="h-5 w-5" />
          </div>
          <div>
            <p className="font-[family-name:var(--font-display)] text-base font-semibold tracking-tight">
              Facturador SIAT
            </p>
            <p className="text-xs text-muted-foreground">Demo Compra-Venta · modalidad 2</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
                  isActive && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground",
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <Separator className="my-4" />
        <div className="space-y-3 px-1">
          <div>
            <p className="text-sm font-medium">{user?.username}</p>
            <p className="truncate text-xs text-muted-foreground">
              {user?.empresa_razon_social ?? `Empresa #${user?.empresa_id ?? "—"}`}
            </p>
          </div>
          <Button variant="outline" className="w-full justify-start" onClick={() => void logout()}>
            <LogOut className="h-4 w-4" />
            Salir
          </Button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex items-center justify-between border-b bg-card/95 px-4 py-3 backdrop-blur md:hidden">
          <div>
            <p className="font-[family-name:var(--font-display)] font-semibold">Facturador SIAT</p>
            <p className="text-xs text-muted-foreground">{user?.username}</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => void logout()}>
            Salir
          </Button>
        </header>
        <nav className="flex gap-1 overflow-x-auto border-b bg-card/80 px-2 py-2 md:hidden">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium text-muted-foreground",
                  isActive && "bg-primary text-primary-foreground",
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 p-4 md:p-0 md:pl-0">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
