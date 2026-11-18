import { Plus, Trash2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ApiError, emitirFactura, fetchClientes, fetchProductos, fetchSucursales } from "@/lib/api"
import type { Cliente, Producto, Sucursal } from "@/lib/types"
import { formatMoney } from "@/lib/utils"

type Linea = {
  key: string
  producto_id: string
  cantidad: string
}

export function EmitirPage() {
  const navigate = useNavigate()
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [productos, setProductos] = useState<Producto[]>([])
  const [sucursales, setSucursales] = useState<Sucursal[]>([])
  const [loading, setLoading] = useState(true)
  const [clienteId, setClienteId] = useState("")
  const [sucursalId, setSucursalId] = useState("")
  const [puntoVentaId, setPuntoVentaId] = useState("")
  const [lineas, setLineas] = useState<Linea[]>([
    { key: crypto.randomUUID(), producto_id: "", cantidad: "1" },
  ])
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [c, p, s] = await Promise.all([fetchClientes(), fetchProductos(), fetchSucursales()])
        if (cancelled) return
        setClientes(c)
        setProductos(p.filter((x) => x.activo))
        setSucursales(s)
        if (c[0]) setClienteId(String(c[0].id))
        if (s[0]) {
          setSucursalId(String(s[0].id))
          const pv = s[0].puntos_venta.find((x) => x.activo) ?? s[0].puntos_venta[0]
          if (pv) setPuntoVentaId(String(pv.id))
        }
        if (p[0]) {
          setLineas([{ key: crypto.randomUUID(), producto_id: String(p[0].id), cantidad: "1" }])
        }
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : "Error al cargar catálogos")
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const puntosVenta = useMemo(() => {
    const s = sucursales.find((x) => String(x.id) === sucursalId)
    return s?.puntos_venta ?? []
  }, [sucursales, sucursalId])

  const total = useMemo(() => {
    return lineas.reduce((acc, line) => {
      const prod = productos.find((p) => String(p.id) === line.producto_id)
      const qty = Number(line.cantidad) || 0
      const price = prod ? Number(prod.precio_unitario) : 0
      return acc + qty * price
    }, 0)
  }, [lineas, productos])

  function updateLinea(key: string, patch: Partial<Linea>) {
    setLineas((prev) => prev.map((l) => (l.key === key ? { ...l, ...patch } : l)))
  }

  async function onSubmit() {
    if (!clienteId || !sucursalId || !puntoVentaId) {
      toast.error("Selecciona cliente, sucursal y punto de venta")
      return
    }
    const payloadLineas = lineas
      .filter((l) => l.producto_id && Number(l.cantidad) > 0)
      .map((l) => ({
        producto_id: Number(l.producto_id),
        cantidad: Number(l.cantidad),
      }))
    if (payloadLineas.length === 0) {
      toast.error("Agrega al menos una línea válida")
      return
    }
    setSubmitting(true)
    try {
      const result = await emitirFactura({
        cliente_id: Number(clienteId),
        sucursal_id: Number(sucursalId),
        punto_venta_id: Number(puntoVentaId),
        lineas: payloadLineas,
      })
      toast.success(`Factura #${result.numero_factura} emitida (stub 908)`)
      navigate(`/facturas/${result.id}`)
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "No se pudo emitir")
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold">Emitir factura</h1>
        <p className="text-sm text-muted-foreground">
          Compra-Venta · envío stub al SIN (código 908)
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Cabecera</CardTitle>
          <CardDescription>Cliente y punto de emisión</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <Label>Cliente</Label>
            <Select value={clienteId} onValueChange={setClienteId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar" />
              </SelectTrigger>
              <SelectContent>
                {clientes.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>
                    {c.razon_social}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Sucursal</Label>
            <Select
              value={sucursalId}
              onValueChange={(v) => {
                setSucursalId(v)
                const s = sucursales.find((x) => String(x.id) === v)
                const pv = s?.puntos_venta.find((x) => x.activo) ?? s?.puntos_venta[0]
                setPuntoVentaId(pv ? String(pv.id) : "")
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar" />
              </SelectTrigger>
              <SelectContent>
                {sucursales.map((s) => (
                  <SelectItem key={s.id} value={String(s.id)}>
                    {s.codigo_sucursal === 0 ? "Casa Matriz" : `Sucursal ${s.codigo_sucursal}`} —{" "}
                    {s.direccion}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Punto de venta</Label>
            <Select value={puntoVentaId} onValueChange={setPuntoVentaId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar" />
              </SelectTrigger>
              <SelectContent>
                {puntosVenta.map((pv) => (
                  <SelectItem key={pv.id} value={String(pv.id)}>
                    {pv.nombre} (#{pv.codigo_punto_venta})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Líneas</CardTitle>
            <CardDescription>Productos y cantidades</CardDescription>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() =>
              setLineas((prev) => [
                ...prev,
                {
                  key: crypto.randomUUID(),
                  producto_id: productos[0] ? String(productos[0].id) : "",
                  cantidad: "1",
                },
              ])
            }
          >
            <Plus className="h-4 w-4" />
            Agregar
          </Button>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Producto</TableHead>
                <TableHead className="w-28">Cantidad</TableHead>
                <TableHead className="w-32">P. unitario</TableHead>
                <TableHead className="w-32">Subtotal</TableHead>
                <TableHead className="w-12" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {lineas.map((line) => {
                const prod = productos.find((p) => String(p.id) === line.producto_id)
                const sub = (Number(line.cantidad) || 0) * (prod ? Number(prod.precio_unitario) : 0)
                return (
                  <TableRow key={line.key}>
                    <TableCell>
                      <Select
                        value={line.producto_id}
                        onValueChange={(v) => updateLinea(line.key, { producto_id: v })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Producto" />
                        </SelectTrigger>
                        <SelectContent>
                          {productos.map((p) => (
                            <SelectItem key={p.id} value={String(p.id)}>
                              {p.descripcion}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        min="0.0001"
                        step="1"
                        value={line.cantidad}
                        onChange={(e) => updateLinea(line.key, { cantidad: e.target.value })}
                      />
                    </TableCell>
                    <TableCell>{prod ? formatMoney(prod.precio_unitario) : "—"}</TableCell>
                    <TableCell>{formatMoney(sub)}</TableCell>
                    <TableCell>
                      <Button
                        type="button"
                        size="icon"
                        variant="ghost"
                        disabled={lineas.length === 1}
                        onClick={() => setLineas((prev) => prev.filter((l) => l.key !== line.key))}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
          <div className="mt-4 flex items-center justify-between border-t pt-4">
            <p className="text-sm text-muted-foreground">Total estimado</p>
            <p className="text-xl font-semibold">{formatMoney(total)}</p>
          </div>
          <div className="mt-4 flex justify-end">
            <Button disabled={submitting} onClick={() => void onSubmit()}>
              {submitting ? "Emitiendo…" : "Emitir factura"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
