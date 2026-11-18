import { useCallback, useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { toast } from "sonner"

import { StatusBadge } from "@/components/StatusBadge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import { anularFactura, ApiError, fetchFactura, pdfUrl, xmlUrl } from "@/lib/api"
import type { ClienteResumen, Factura } from "@/lib/types"
import { formatMoney } from "@/lib/utils"

function clienteInfo(cliente: Factura["cliente"]) {
  if (typeof cliente === "object" && cliente !== null) {
    const c = cliente as ClienteResumen
    return `${c.razon_social} (${c.numero_documento})`
  }
  return `Cliente #${cliente}`
}

export function FacturaDetallePage() {
  const { id } = useParams()
  const facturaId = Number(id)
  const [factura, setFactura] = useState<Factura | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [open, setOpen] = useState(false)
  const [motivoCodigo, setMotivoCodigo] = useState("1")
  const [motivoDesc, setMotivoDesc] = useState("")
  const [anulando, setAnulando] = useState(false)

  const load = useCallback(async () => {
    if (!Number.isFinite(facturaId)) {
      setError("Identificador inválido")
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await fetchFactura(facturaId)
      setFactura(data)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar la factura")
      setFactura(null)
    } finally {
      setLoading(false)
    }
  }, [facturaId])

  useEffect(() => {
    void load()
  }, [load])

  async function onAnular() {
    setAnulando(true)
    try {
      const res = await anularFactura(facturaId, motivoCodigo, motivoDesc)
      toast.success(res.mensaje || "Factura anulada")
      setOpen(false)
      await load()
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "No se pudo anular")
    } finally {
      setAnulando(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Button asChild variant="ghost" size="sm" className="-ml-2 mb-1">
            <Link to="/facturas">← Volver</Link>
          </Button>
          <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold">
            Factura {factura ? `#${factura.numero_factura}` : ""}
          </h1>
        </div>
        {factura && (
          <div className="flex flex-wrap gap-2">
            <Button asChild variant="outline">
              <a href={pdfUrl(factura.id)} target="_blank" rel="noreferrer">
                Descargar PDF
              </a>
            </Button>
            <Button asChild variant="outline">
              <a href={xmlUrl(factura.id)} target="_blank" rel="noreferrer">
                Ver XML
              </a>
            </Button>
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button variant="destructive">Anular</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Anular factura</DialogTitle>
                  <DialogDescription>
                    La anulación respeta el plazo y motivos del caso de uso SIAT.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label htmlFor="motivo">Código motivo</Label>
                    <Input
                      id="motivo"
                      value={motivoCodigo}
                      onChange={(e) => setMotivoCodigo(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="desc">Descripción</Label>
                    <Textarea
                      id="desc"
                      value={motivoDesc}
                      onChange={(e) => setMotivoDesc(e.target.value)}
                      placeholder="Motivo de anulación"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setOpen(false)}>
                    Cancelar
                  </Button>
                  <Button variant="destructive" disabled={anulando} onClick={() => void onAnular()}>
                    {anulando ? "Anulando…" : "Confirmar anulación"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        )}
      </div>

      {loading ? (
        <Skeleton className="h-48 w-full" />
      ) : error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : factura ? (
        <Card>
          <CardHeader>
            <CardTitle>Detalle</CardTitle>
            <CardDescription>Datos de emisión y estado ante el SIN (stub)</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs uppercase text-muted-foreground">Cliente</p>
              <p className="font-medium">{clienteInfo(factura.cliente)}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-muted-foreground">Monto</p>
              <p className="font-medium">{formatMoney(factura.monto_total)}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-muted-foreground">Estado interno</p>
              <StatusBadge value={factura.estado_interno} />
            </div>
            <div>
              <p className="text-xs uppercase text-muted-foreground">Estado SIAT</p>
              <StatusBadge value={factura.estado_siat} />
            </div>
            <div className="sm:col-span-2">
              <p className="text-xs uppercase text-muted-foreground">CUF</p>
              <p className="break-all font-mono text-sm">{factura.cuf || "—"}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-muted-foreground">Recepción</p>
              <p className="font-mono text-sm">{factura.codigo_recepcion || "—"}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-muted-foreground">Offline</p>
              <p>{factura.offline_flag ? "Sí" : "No"}</p>
            </div>
            {factura.errores_siat && (
              <div className="sm:col-span-2">
                <p className="text-xs uppercase text-muted-foreground">Errores SIAT</p>
                <Alert variant="destructive" className="mt-1">
                  <AlertDescription>{factura.errores_siat}</AlertDescription>
                </Alert>
              </div>
            )}
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
