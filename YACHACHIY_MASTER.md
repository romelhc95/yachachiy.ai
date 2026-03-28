# YACHACHIY_MASTER: Especificación y Estado de Yachachiy.ai

## Visión: "Google Flights de la Educación Tecnológica en Perú"
## Stack: Next.js 14, FastAPI, PostgreSQL 16 (Producción) / SQLite (Desarrollo Local), Redis, Playwright.

## Roles y Responsabilidades Autónomas:
- @planner: Director Supremo. Orquesta el workflow, crea nuevos agentes si es necesario y reevalúa el progreso.
- @architect: Diseño de sistemas y documentación técnica (list_directory, replace).
- @data-harvester: Extracción de datos autónoma con Playwright.
- @ai-parser: Estandarización de datos con IA.
- @backend-core: Desarrollo de APIs asíncronas.
- @frontend-master: UI/UX con Shadcn/UI y Tailwind (replace).
- @security-auditor: Filtro de seguridad (Bloqueo obligatorio).
- @tdd-lead: Guardián de calidad (Bloqueo obligatorio).

## Plan de Fases:
- Fase 1: Harvester Pilot (Completada).
- Fase 2: Search UI & API (Completada).
- Fase 3: Conversión (Captura de Leads y Detalle) (Completada).
- Fase 4: Inteligencia (Cálculo de ROI Académico) (Completada).
- Fase 5: Expansión (Comparador y Versión Mobile) (Completada).

## Reglas de Oro del Workflow:
1. PROHIBIDO pasar a la siguiente fase sin validación 100% de @security-auditor y @tdd-lead.
2. DOCUMENTACIÓN: Todo reporte, README y commit debe ser en ESPAÑOL.
3. PERSISTENCIA: Realizar push a GitHub tras cada validación de fase exitosa.
