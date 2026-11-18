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
  createCliente,
  deleteCliente,
  fetchClientes,
  updateCliente,
} from "@/lib/api"
import type { Cliente } from "@/lib/types"

const emptyForm = {
  codigo_cliente: "",
  tipo_documento_identidad: 5,
  numero_documento: "",
  complemento: "",
  razon_social: "",
  email: "",
}

export function ClientesPage() {
  const [rows, setRows] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Cliente | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  async function load() {
    setLoading(true)
    try {
      setRows(await fetchClientes())
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Error al listar clientes")
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

  function openEdit(c: Cliente) {
    setEditing(c)
    setForm({
      codigo_cliente: c.codigo_cliente,
      tipo_documento_identidad: c.tipo_documento_identidad,
      numero_documento: c.numero_documento,
      complemento: c.complemento || "",
      razon_social: c.razon_social,
      email: c.email || "",
    })
    setOpen(true)
  }

  async function onSave() {
    setSaving(true)
    try {
      if (editing) {
        await updateCliente(editing.id, form)
        toast.success("Cliente actualizado")
      } else {
        await createCliente(form)
        toast.success("Cliente creado")
      }
      setOpen(false)
      await load()
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "No se pudo guardar")
    } finally {
      setSaving(false)
    }
  }

  async function onDelete(c: Cliente) {
    if (!confirm(`¿Eliminar cliente ${c.razon_social}?`)) return
    try {
      await deleteCliente(c.id)
      toast.success("Cliente eliminado")
      await load()
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "No se pudo eliminar")
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold">Clientes</h1>
          <p className="text-sm text-muted-foreground">ABM multi-tenant de la empresa</p>
        </div>
        <Button onClick={openCreate}>Nuevo cliente</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Listado</CardTitle>
          <CardDescription>{rows.length} cliente(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-32 w-full" />
          ) : rows.length === 0 ? (
            <p className="py-10 text-center text-sm text-muted-foreground">No hay clientes.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Razón social</TableHead>
                  <TableHead>Documento</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell>{c.codigo_cliente}</TableCell>
                    <TableCell className="font-medium">{c.razon_social}</TableCell>
                    <TableCell>
                      {c.numero_documento}
                      {c.complemento ? `-${c.complemento}` : ""}
                    </TableCell>
                    <TableCell>{c.email || "—"}</TableCell>
                    <TableCell className="space-x-1 text-right">
                      <Button size="sm" variant="ghost" onClick={() => openEdit(c)}>
                        Editar
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => void onDelete(c)}>
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
            <DialogTitle>{editing ? "Editar cliente" : "Nuevo cliente"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Código</Label>
              <Input
                value={form.codigo_cliente}
                onChange={(e) => setForm({ ...form, codigo_cliente: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Tipo doc.</Label>
              <Input
                type="number"
                value={form.tipo_documento_identidad}
                onChange={(e) =>
                  setForm({ ...form, tipo_documento_identidad: Number(e.target.value) })
                }
              />
            </div>
            <div className="space-y-2">
              <Label>Nº documento</Label>
              <Input
                value={form.numero_documento}
                onChange={(e) => setForm({ ...form, numero_documento: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Complemento</Label>
              <Input
                value={form.complemento}
                onChange={(e) => setForm({ ...form, complemento: e.target.value })}
              />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label>Razón social</Label>
              <Input
                value={form.razon_social}
                onChange={(e) => setForm({ ...form, razon_social: e.target.value })}
              />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label>Email</Label>
              <Input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
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
