# Checklist operativo — Piloto SIAT

Este documento **no aprueba** el sistema ante el SIN. Es una guía para que Jose ejecute pruebas cuando ya tenga autorización.

Enlaces oficiales (siatinfo):

- [Fase I / batería de pruebas](https://siatinfo.impuestos.gob.bo/) — confirmar Excel oficial (umbrales por verificar)
- [Proceso de autorización](https://siatinfo.impuestos.gob.bo/)
- [Token delegado](https://siatinfo.impuestos.gob.bo/)
- Anexo Técnico Ley N.° 1733 y **RND 102600000045** (prórroga del piloto hasta el D.S. reglamentario; mientras tanto rige RND 102100000011) — **por verificar vigencia cada semana**

No inventes WSDL ni NIT “oficiales”. No commitees evidencias con datos reales, tokens o XML de contribuyentes.

---

## A. Previos

| # | Ítem | Hecho | Evidencia |
|---|------|-------|-----------|
| A1 | NIT activo con obligación IVA y sin marcas | ☐ | |
| A2 | Tipo Proveedor si el SaaS lo usarán terceros | ☐ | |
| A3 | Sistema registrado en Gestión de Autorización (PILOTO) | ☐ | |
| A4 | WSDL del reporte pegados en `.env` (ya no `POR_COMPLETAR`) | ☐ | |
| A5 | Token delegado solo en entorno (nunca en git) | ☐ | |
| A6 | XSD oficial Compra-Venta en `schemas/` | ☐ | |
| A7 | `SIAT_AMBIENTE` contrastado con WSDL (por verificar 1/2 vs 1/2/3) | ☐ | |
| A8 | CAFC solicitado si se probarán eventos 5–7 | ☐ | |

---

## B. Fase I (volúmenes — confirmar en Excel del SIN; pueden cambiar)

| Caso | Descripción | Volumen citado | Hecho | Evidencia (id request / recepción / captura) |
|------|-------------|----------------|-------|-----------------------------------------------|
| I | CUIS | 2 por caso | ☐ | |
| II | Catálogos | 50 por caso | ☐ | |
| III | CUFD | 100 por caso | ☐ | |
| IV | Emisión individual (sector 1; 24 si declaró NCD) | 500 | ☐ | |
| V | Eventos significativos | 5 por caso | ☐ | |
| VI | Paquetes de contingencia | 10 por caso | ☐ | |
| VII | Anulación | 250 | ☐ | |
| VIII | Firma digital | Electrónica; Computarizada **por verificar** si el portal la exige | ☐ | |
| IX–X | Masiva / IEHD | Fuera del MVP salvo marca en autorización | ☐ | |
| XI | Reversión de anulación | 98 | ☐ | |

---

## C. Fase II

| # | Ítem | Hecho | Evidencia |
|---|------|-------|-----------|
| C1 | Nominatividad | ☐ | |
| C2 | Monto 0 / Gift Card | ☐ | |
| C3 | Medios de pago | ☐ | |
| C4 | Leyendas | ☐ | |
| C5 | Máscara de tarjeta | ☐ | |
| C6 | Plazos 48 h / 72 h | ☐ | |
| C7 | Anulación hasta día 9 del mes siguiente | ☐ | |
| C8 | CAFC / transcripción | ☐ | |
| C9 | Envío PDF+XML al comprador | ☐ | |
| C10 | Contingencia automática | ☐ | |

---

## D. Fase III (proveedor)

| # | Ítem | Hecho | Evidencia |
|---|------|-------|-----------|
| D1 | Asociación NIT cliente | ☐ | |
| D2 | Confirmación | ☐ | |
| D3 | Token delegado del cliente (nunca mezclar tokens entre empresas) | ☐ | |
| D4 | Catálogo / emisión / anulación / reversión | ☐ | |
| D5 | Eventos / paquetes / transcripción CAFC | ☐ | |
| D6 | Recordatorio: iniciar operaciones es declaración jurada | ☐ | |

---

## E. Bitácora

- Guardar evidencias **fuera del repo** o anonimizadas.
- No imprimir el token en logs ni capturas.
- Completar campo evidencia con id de request, código de recepción o captura.

---

## Comando de apoyo (opcional)

```bash
# Solo con .env real; se niega en CI o si falta WSDL/token
python manage.py siat_piloto_smoke --subset cuis
```
