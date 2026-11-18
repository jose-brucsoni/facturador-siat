import { useEffect, useState } from "react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
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
import { ApiError, fetchConfig } from "@/lib/api"
import type { ConfigStatus } from "@/lib/types"

export function ConfigPage() {
  const [data, setData] = useState<ConfigStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const cfg = await fetchConfig()
        if (!cancelled) setData(cfg)
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : "Error al cargar config")
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
        <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold">
          Configuración SIAT
        </h1>
        <p className="text-sm text-muted-foreground">
          Solo lectura. El token nunca se muestra en claro.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Variables de entorno</CardTitle>
          <CardDescription>Completitud y valores seguros (enmascarados)</CardDescription>
        </CardHeader>
        <CardContent>
          {loading || !data ? (
            <Skeleton className="h-40 w-full" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Variable</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Valor seguro</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.keys(data.valores_seguros).map((key) => {
                  const estado = data.completitud[key] ?? "—"
                  const ok = estado === "ok"
                  return (
                    <TableRow key={key}>
                      <TableCell className="font-mono text-xs">{key}</TableCell>
                      <TableCell>
                        <Badge variant={ok ? "success" : "warning"}>{estado}</Badge>
                      </TableCell>
                      <TableCell className="max-w-md truncate font-mono text-xs">
                        {data.valores_seguros[key]}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
