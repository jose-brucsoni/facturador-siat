import { Badge } from "@/components/ui/badge"

function variantFor(estado: string): "success" | "warning" | "danger" | "secondary" {
  const e = estado.toLowerCase()
  if (e.includes("acept") || e.includes("valid") || e === "emitida" || e === "ok") return "success"
  if (e.includes("anul") || e.includes("rechaz") || e.includes("error")) return "danger"
  if (e.includes("pend") || e.includes("envi") || e.includes("proceso")) return "warning"
  return "secondary"
}

export function StatusBadge({ value }: { value: string }) {
  if (!value) return <Badge variant="secondary">—</Badge>
  return <Badge variant={variantFor(value)}>{value}</Badge>
}
