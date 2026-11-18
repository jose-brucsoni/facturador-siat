# Frontend — Facturador SIAT

SPA React + Vite + Tailwind CSS + shadcn/ui.

## Desarrollo

```bash
npm install
npm run dev
```

Abre http://127.0.0.1:5173/ con Django en `:8000` (`python manage.py runserver`). El proxy de Vite reenvía `/api` al backend.

## Build

```bash
npm run build
```

Django sirve `dist/` en producción/demo unificada.
