import { useEffect, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  ApiError,
  createProducto,
  deleteProducto,
  fetchProductos,
  updateProducto,
} from "@/lib/api"
import type { Producto } from "@/lib/types"
import { formatMoney } from "@/lib/utils"

const emptyForm = {
  codigo_interno: "",
  descripcion: "",
  actividad_economica: "",
  codigo_producto_sin: "",
  unidad_medida: 58,
  precio_unitario: "0",
  activo: true,
}

export function ProductosPage() {
  const [rows, setRows] = useState<Producto[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Producto | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  async function load() {
    setLoading(true)
    try {
      setRows(await fetchProductos())
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Error al listar productos")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  function openCreate() {
    setEditing(null)
    setForm(emptyForm)
    setOpen(true)
  }

  function openEdit(p: Producto) {
    setEditing(p)
    setForm({
      codigo_interno: p.codigo_interno,
      descripcion: p.descripcion,
      actividad_economica: p.actividad_economica,
      codigo_producto_sin: p.codigo_producto_sin,
      unidad_medida: p.unidad_medida,
      precio_unitario: p.precio_unitario,
      activo: p.activo,
    })
    setOpen(true)
  }

  async function onSave() {
    setSaving(true)
    try {
      if (editing) {
        await updateProducto(editing.id, form)
        toast.success("Producto actualizado")
      } else {
        await createProducto(form)
        toast.success("Producto creado")
      }
      setOpen(false)
      await load()
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "No se pudo guardar")
    } finally {
      setSaving(false)
    }
  }

  async function onDelete(p: Producto) {
    if (!confirm(`¿Eliminar producto ${p.descripcion}?`)) return
    try {
      await deleteProducto(p.id)
      toast.success("Producto eliminado")
      await load()
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "No se pudo eliminar")
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold">Productos</h1>
          <p className="text-sm text-muted-foreground">Catálogo interno de la empresa</p>
        </div>
        <Button onClick={openCreate}>Nuevo producto</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Listado</CardTitle>
          <CardDescription>{rows.length} producto(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-32 w-full" />
          ) : rows.length === 0 ? (
            <p className="py-10 text-center text-sm text-muted-foreground">No hay productos.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Precio</TableHead>
                  <TableHead>Activo</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>{p.codigo_interno}</TableCell>
                    <TableCell className="font-medium">{p.descripcion}</TableCell>
                    <TableCell>{formatMoney(p.precio_unitario)}</TableCell>
                    <TableCell>{p.activo ? "Sí" : "No"}</TableCell>
                    <TableCell className="space-x-1 text-right">
                      <Button size="sm" variant="ghost" onClick={() => openEdit(p)}>
                        Editar
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => void onDelete(p)}>
                        Eliminar
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Editar producto" : "Nuevo producto"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Código interno</Label>
              <Input
                value={form.codigo_interno}
                onChange={(e) => setForm({ ...form, codigo_interno: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Precio unitario</Label>
              <Input
                value={form.precio_unitario}
                onChange={(e) => setForm({ ...form, precio_unitario: e.target.value })}
              />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label>Descripción</Label>
              <Input
                value={form.descripcion}
                onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Actividad económica</Label>
              <Input
                value={form.actividad_economica}
                onChange={(e) => setForm({ ...form, actividad_economica: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Código producto SIN</Label>
              <Input
                value={form.codigo_producto_sin}
                onChange={(e) => setForm({ ...form, codigo_producto_sin: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Unidad de medida</Label>
              <Input
                type="number"
                value={form.unidad_medida}
                onChange={(e) => setForm({ ...form, unidad_medida: Number(e.target.value) })}
              />
            </div>
            <div className="flex items-end gap-2">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.activo}
                  onChange={(e) => setForm({ ...form, activo: e.target.checked })}
                />
                Activo
              </label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button disabled={saving} onClick={() => void onSave()}>
              {saving ? "Guardando…" : "Guardar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
