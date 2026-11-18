export type UserSession = {
  username: string
  empresa_id: number | null
  empresa_razon_social?: string | null
}

export type Cliente = {
  id: number
  codigo_cliente: string
  tipo_documento_identidad: number
  numero_documento: string
  complemento: string
  razon_social: string
  email: string
  nit_validado: boolean
}

export type Producto = {
  id: number
  codigo_interno: string
  descripcion: string
  actividad_economica: string
  codigo_producto_sin: string
  unidad_medida: number
  precio_unitario: string
  activo: boolean
}

export type ClienteResumen = {
  id: number
  razon_social: string
  numero_documento: string
}

export type Factura = {
  id: number
  numero_factura: number
  cuf: string
  fecha_emision: string
  monto_total: string
  estado_interno: string
  estado_siat: string
  codigo_recepcion: string
  errores_siat: string
  cliente: number | ClienteResumen
  offline_flag: boolean
}

export type PuntoVenta = {
  id: number
  codigo_punto_venta: number
  nombre: string
  activo: boolean
}

export type Sucursal = {
  id: number
  codigo_sucursal: number
  direccion: string
  municipio: string
  activa: boolean
  puntos_venta: PuntoVenta[]
}

export type ConfigStatus = {
  completitud: Record<string, string>
  valores_seguros: Record<string, string>
}

export type EmitirPayload = {
  cliente_id: number
  sucursal_id: number
  punto_venta_id: number
  lineas: Array<{
    producto_id: number
    cantidad: number
    precio_unitario?: number
  }>
}

export type EmitirResult = {
  id: number
  estado_interno: string
  estado_siat: string
  cuf: string
  numero_factura: number
  pdf_url: string
  offline: boolean
}

export type ApiErrorBody = {
  detail?: string
  [key: string]: unknown
}
