import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"

import { StatusBadge } from "@/components/StatusBadge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
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
import type { ClienteResumen, Factura } from "@/lib/types"
import { formatMoney, truncate } from "@/lib/utils"

function clienteLabel(cliente: Factura["cliente"]): string {
  if (typeof cliente === "object" && cliente !== null) {
    return (cliente as ClienteResumen).razon_social
  }
  return `#${cliente}`
}

export function FacturasPage() {
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState("")

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const data = await fetchFacturas()
        if (!cancelled) setFacturas(data)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const filtered = useMemo(() => {
    const term = q.trim().toLowerCase()
    if (!term) return facturas
    return facturas.filter((f) => {
      const cliente = clienteLabel(f.cliente).toLowerCase()
      return (
        String(f.numero_factura).includes(term) ||
        (f.cuf || "").toLowerCase().includes(term) ||
        (f.estado_interno || "").toLowerCase().includes(term) ||
        (f.estado_siat || "").toLowerCase().includes(term) ||
        cliente.includes(term)
      )
    })
  }, [facturas, q])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold">Facturas</h1>
          <p className="text-sm text-muted-foreground">Historial filtrado por tu empresa</p>
        </div>
        <Button asChild>
          <Link to="/emitir">Emitir</Link>
        </Button>
      </div>

      <Card>
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle>Listado</CardTitle>
            <CardDescription>{filtered.length} resultado(s)</CardDescription>
          </div>
          <Input
            className="sm:max-w-xs"
            placeholder="Buscar por Nº, CUF, cliente o estado…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : filtered.length === 0 ? (
            <p className="py-10 text-center text-sm text-muted-foreground">Sin facturas para mostrar.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nº</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>CUF</TableHead>
                  <TableHead>Monto</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>SIAT</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell className="font-medium">{f.numero_factura}</TableCell>
                    <TableCell className="text-xs">
                      {f.fecha_emision ? new Date(f.fecha_emision).toLocaleString("es-BO") : "—"}
                    </TableCell>
                    <TableCell>{clienteLabel(f.cliente)}</TableCell>
                    <TableCell className="font-mono text-xs">{truncate(f.cuf || "—", 16)}</TableCell>
                    <TableCell>{formatMoney(f.monto_total)}</TableCell>
                    <TableCell>
                      <StatusBadge value={f.estado_interno} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={f.estado_siat} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button asChild size="sm" variant="ghost">
                        <Link to={`/facturas/${f.id}`}>Detalle</Link>
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
