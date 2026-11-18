import { FileText, PlusCircle, Settings, Users } from "lucide-react"
import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { StatusBadge } from "@/components/StatusBadge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { fetchFacturas } from "@/lib/api"
import { useAuth } from "@/lib/auth"
import type { Factura } from "@/lib/types"
import { formatMoney, truncate } from "@/lib/utils"

export function DashboardPage() {
  const { user } = useAuth()
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const data = await fetchFacturas()
        if (!cancelled) setFacturas(data.slice(0, 8))
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold tracking-tight">
          Inicio
        </h1>
        <p className="text-sm text-muted-foreground">
          {user?.empresa_razon_social ?? "Empresa"} · caja demo Compra-Venta
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Emisión</CardDescription>
            <CardTitle className="text-base">Nueva factura</CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link to="/emitir">
                <PlusCircle className="h-4 w-4" />
                Emitir
              </Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Historial</CardDescription>
            <CardTitle className="text-base">Facturas</CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full">
              <Link to="/facturas">
                <FileText className="h-4 w-4" />
                Ver listado
              </Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Maestros</CardDescription>
            <CardTitle className="text-base">Clientes</CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full">
              <Link to="/clientes">
                <Users className="h-4 w-4" />
                Administrar
              </Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>SIAT</CardDescription>
            <CardTitle className="text-base">Configuración</CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild variant="outline" className="w-full">
              <Link to="/config">
                <Settings className="h-4 w-4" />
                Revisar
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Últimas facturas</CardTitle>
          <CardDescription>Resumen reciente de la empresa autenticada</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : facturas.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Aún no hay facturas. Emite la primera desde la caja.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nº</TableHead>
                  <TableHead>CUF</TableHead>
                  <TableHead>Monto</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>SIAT</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {facturas.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell className="font-medium">{f.numero_factura}</TableCell>
                    <TableCell className="font-mono text-xs">{truncate(f.cuf || "—", 18)}</TableCell>
                    <TableCell>{formatMoney(f.monto_total)}</TableCell>
                    <TableCell>
                      <StatusBadge value={f.estado_interno} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={f.estado_siat} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button asChild variant="ghost" size="sm">
                        <Link to={`/facturas/${f.id}`}>Ver</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
