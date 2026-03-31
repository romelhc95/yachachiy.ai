# YACHACHIY_MASTER: Especificación y Estado Final de Yachachiy.ai (2025)

## Visión: "Google Flights de la Educación Superior en Perú"
## Stack Final: Next.js 15 (Cloudflare Pages), Supabase Serverless (PostgreSQL), IA-Powered Scrapers (Playwright + AI Parser).

## Arquitectura de Nueva Generación:
- **Frontend & Routing:** Next.js 15 con App Router y Server Components.
- **Data Persistence:** Supabase Cloud con RLS (Row Level Security).
- **Security:** Bypass de backend tradicional para comunicación directa Cliente-DB con Anon Key endurecida.
- **Ingestión de Datos:** Automatización vía Python scripts (Harvester/Parser) con UPSERT directo a la nube.

## Estado del Proyecto (Certificado):
- [X] **Fase 1: Harvester Pilot** - 36 Instituciones mapeadas.
- [X] **Fase 2: Search UI & API** - Interfaz de búsqueda ultrarrápida con Shadcn/UI.
- [X] **Fase 3: Conversión (Leads)** - Formulario hermético protegido por RLS.
- [X] **Fase 4: Inteligencia (ROI)** - Cálculo de retorno de inversión por curso.
- [X] **Fase 5: Expansión** - Comparador y vista de detalle completa.
- [X] **Certificación Final** - Validado por @tdd-lead y @security-auditor.

## Mapa Institucional:
- **Instituciones:** 36.
- **Cursos Piloto:** 19.
- **Flujo de Lead:** POST a 'leads' verificado; GET restringido.

