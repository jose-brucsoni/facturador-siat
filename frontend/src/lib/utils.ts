import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatMoney(value: string | number): string {
  const n = typeof value === "string" ? Number(value) : value
  if (Number.isNaN(n)) return String(value)
  return new Intl.NumberFormat("es-BO", {
    style: "currency",
    currency: "BOB",
    minimumFractionDigits: 2,
  }).format(n)
}

export function truncate(value: string, max = 24): string {
  if (value.length <= max) return value
  return `${value.slice(0, max)}…`
}
