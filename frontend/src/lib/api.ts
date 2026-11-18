import type {
  ApiErrorBody,
  Cliente,
  ConfigStatus,
  EmitirPayload,
  EmitirResult,
  Factura,
  Producto,
  Sucursal,
  UserSession,
} from "@/lib/types"

export class ApiError extends Error {
  status: number
  body: ApiErrorBody | null

  constructor(message: string, status: number, body: ApiErrorBody | null = null) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.body = body
  }
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

async function parseJson<T>(res: Response): Promise<T | null> {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text) as T
  } catch {
    return null
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)
  if (!headers.has("Accept")) headers.set("Accept", "application/json")

  const method = (options.method ?? "GET").toUpperCase()
  if (method !== "GET" && method !== "HEAD") {
    const csrf = getCookie("csrftoken")
    if (csrf) headers.set("X-CSRFToken", csrf)
    if (options.body && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json")
    }
  }

  const res = await fetch(path, {
    ...options,
    headers,
    credentials: "include",
  })

  if (res.status === 204) return undefined as T

  const contentType = res.headers.get("content-type") ?? ""
  if (!contentType.includes("application/json")) {
    if (!res.ok) {
      throw new ApiError(`Error HTTP ${res.status}`, res.status)
    }
    return undefined as T
  }

  const body = await parseJson<T | ApiErrorBody>(res)
  if (!res.ok) {
    const err = (body ?? {}) as ApiErrorBody
    throw new ApiError(err.detail ?? `Error HTTP ${res.status}`, res.status, err)
  }
  return body as T
}

export async function ensureCsrf(): Promise<void> {
  await apiFetch<{ csrfToken: string }>("/api/v1/csrf/")
}

export async function login(username: string, password: string): Promise<UserSession> {
  await ensureCsrf()
  return apiFetch<UserSession>("/api/v1/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  })
}

export async function logout(): Promise<void> {
  await apiFetch("/api/v1/logout/", { method: "POST" })
}

export async function fetchMe(): Promise<UserSession> {
  return apiFetch<UserSession>("/api/v1/me/")
}

export async function fetchConfig(): Promise<ConfigStatus> {
  return apiFetch<ConfigStatus>("/api/v1/config/")
}

export async function fetchClientes(): Promise<Cliente[]> {
  return apiFetch<Cliente[]>("/api/v1/clientes/")
}

export async function createCliente(data: Partial<Cliente>): Promise<Cliente> {
  return apiFetch<Cliente>("/api/v1/clientes/", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

export async function updateCliente(id: number, data: Partial<Cliente>): Promise<Cliente> {
  return apiFetch<Cliente>(`/api/v1/clientes/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  })
}

export async function deleteCliente(id: number): Promise<void> {
  await apiFetch(`/api/v1/clientes/${id}/`, { method: "DELETE" })
}

export async function fetchProductos(): Promise<Producto[]> {
  return apiFetch<Producto[]>("/api/v1/productos/")
}

export async function createProducto(data: Partial<Producto>): Promise<Producto> {
  return apiFetch<Producto>("/api/v1/productos/", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

export async function updateProducto(id: number, data: Partial<Producto>): Promise<Producto> {
  return apiFetch<Producto>(`/api/v1/productos/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  })
}

export async function deleteProducto(id: number): Promise<void> {
  await apiFetch(`/api/v1/productos/${id}/`, { method: "DELETE" })
}

export async function fetchFacturas(): Promise<Factura[]> {
  return apiFetch<Factura[]>("/api/v1/facturas/")
}

export async function fetchFactura(id: number): Promise<Factura> {
  return apiFetch<Factura>(`/api/v1/facturas/${id}/`)
}

export async function anularFactura(
  id: number,
  motivo_codigo: string,
  motivo_descripcion: string,
): Promise<{ ok: boolean; mensaje: string }> {
  return apiFetch(`/api/v1/facturas/${id}/anular/`, {
    method: "POST",
    body: JSON.stringify({ motivo_codigo, motivo_descripcion }),
  })
}

export async function fetchSucursales(): Promise<Sucursal[]> {
  return apiFetch<Sucursal[]>("/api/v1/sucursales/")
}

export async function emitirFactura(payload: EmitirPayload): Promise<EmitirResult> {
  return apiFetch<EmitirResult>("/api/v1/emitir/", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function pdfUrl(id: number): string {
  return `/api/v1/facturas/${id}/pdf/`
}

export function xmlUrl(id: number): string {
  return `/api/v1/facturas/${id}/xml/`
}
