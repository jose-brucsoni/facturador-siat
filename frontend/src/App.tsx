import { Navigate, Outlet, Route, Routes } from "react-router-dom"

import { AppShell } from "@/components/layout/AppShell"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/lib/auth"
import { ClientesPage } from "@/pages/ClientesPage"
import { ConfigPage } from "@/pages/ConfigPage"
import { DashboardPage } from "@/pages/DashboardPage"
import { EmitirPage } from "@/pages/EmitirPage"
import { FacturaDetallePage } from "@/pages/FacturaDetallePage"
import { FacturasPage } from "@/pages/FacturasPage"
import { LoginPage } from "@/pages/LoginPage"
import { ProductosPage } from "@/pages/ProductosPage"

function ProtectedRoute() {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-8">
        <Skeleton className="h-12 w-64" />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return <Outlet />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="emitir" element={<EmitirPage />} />
          <Route path="facturas" element={<FacturasPage />} />
          <Route path="facturas/:id" element={<FacturaDetallePage />} />
          <Route path="clientes" element={<ClientesPage />} />
          <Route path="productos" element={<ProductosPage />} />
          <Route path="config" element={<ConfigPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
