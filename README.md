# Yachachiy.ai - El "Google Flights" de la Educación en Latinoamérica

Yachachiy.ai es una plataforma diseñada para centralizar, comparar y optimizar la búsqueda de ofertas educativas en Latinoamérica, comenzando con un enfoque estratégico en el mercado peruano.

## 🚀 Fases del Proyecto (Completadas)
- **Fase 1: Recolección Piloto**: Extracción de datos de universidades principales (UTEC/UPC).
- **Fase 2: API & Search UI**: Desarrollo del backend FastAPI y buscador principal.
- **Fase 3: Detalle & Leads**: Captura de interesados y páginas de detalle.
- **Fase 4: ROI Académico**: Cálculo inteligente del retorno de inversión.
- **Fase 5: Comparador & Mobile**: Herramienta de comparación y diseño responsivo.

## 🛠️ Cómo visualizar e interactuar con Yachachiy.ai

### 1. Requisitos
- Python 3.10+
- Node.js 18+
- SQLite (integrado)

### 2. Ejecución Local
*   **Backend (Puerto 8000):**
    ```powershell
    uvicorn api.main:app --reload
    ```
*   **Frontend (Puerto 3000):**
    ```powershell
    cd web; npm run dev
    ```

## 🚀 Despliegue en la Nube

El proyecto está preparado para ser desplegado de forma gratuita:

### 1. Base de Datos (Supabase)
- Se ha migrado la base de datos a **Supabase (PostgreSQL)**.
- El script `scripts/migrate_db.py` puede usarse para inicializar el esquema en nuevos entornos.

### 2. Backend (Render)
- Conecta este repositorio a [Render](https://render.com).
- Usa el archivo `render.yaml` o configura:
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
  - **Env Vars**: `DATABASE_URL` (tu connection string de Supabase).

### 3. Frontend (Cloudflare Pages)
- Conecta este repositorio a [Cloudflare Pages](https://pages.cloudflare.com/).
- **Configuración Crítica (Panel de Cloudflare):**
  - **Framework preset**: `Next.js (App Router)`
  - **Build command**: `npm run build`
  - **Output directory**: `out`
  - **Root directory**: `web`
- **Limpieza de Entorno:** Si el build falla por "recursive call", asegúrate de que el campo 'Build command' sea estrictamente `npm run build` y no incluya scripts de despliegue recursivo.
- **Troubleshooting de Visibilidad (URL):**
  - **Variable $CF_PAGES_URL vacía:** Es común en el primer build o en ramas no productivas. Revisa los logs para ver el "Enlace sugerido" basado en el nombre del proyecto.
  - **Mensaje "No URLs enabled":** Ve a **Settings > Domains** en tu proyecto de Cloudflare Pages. Verifica que el subdominio `.pages.dev` esté habilitado. Si dice **Disabled**, actívalo para que la URL sea pública.
- **Env Vars**: `NEXT_PUBLIC_API_URL` -> `https://yachachiy-api.onrender.com`

### 4. Migración de Worker a Pages (IMPORTANTE)
Si tu URL termina en `.workers.dev` y muestra "Hello world", has desplegado un **Worker** genérico en lugar de la aplicación **Pages**. Sigue estos pasos:

1.  **Eliminar el Worker**: Ve a tu panel de Cloudflare > Workers & Pages > Selecciona el worker `yachachiy` > Settings > 'Delete'.
2.  **Crear Proyecto de Pages**:
    - Ve a `Workers & Pages` > `Create` > `Pages` > `Connect to Git`.
    - Selecciona tu repositorio `yachachiy_ai`.
3.  **Configuración de Build**:
    - **Framework preset**: `Next.js`
    - **Root directory**: `web`
    - **Build command**: `npm run build`
    - **Output directory**: `out`
4.  **Variables de Entorno**: No olvides añadir `NEXT_PUBLIC_API_URL` en la pestaña 'Settings' > 'Environment Variables' del proyecto de Pages.

## 📜 Control de Versionamiento y Cambios
Registro de hitos y modificaciones significativas en el proyecto:

| Fecha | Versión | Tipo | Descripción de Cambios |
| :--- | :--- | :--- | :--- |
| 28/03/2026 | v1.4.0 | Bug Fix | **Final Fix for Reload Loop**: Implementación definitiva de `React.use()` para la resolución de `params` en Next.js 16 y optimización de la estabilidad en el ciclo de vida de `useEffect`. |
| 28/03/2026 | v1.3.9 | Bug Fix | **Fix Infinite Loop**: Solución del bucle de recarga en el detalle de cursos mediante la correcta gestión de `params` (Promise) en Next.js 15 y limpieza de `useEffect`. |
| 28/03/2026 | v1.3.8 | Bug Fix | **Separación Client/Server**: Refactorización de `/courses/[slug]` para corregir la coexistencia entre `'use client'` y `generateStaticParams` en exportación estática. |
| 28/03/2026 | v1.3.7 | Infra | **Final Fixes**: Optimización de inicio no bloqueante para Render y validación de `generateStaticParams` para Cloudflare. |
| 28/03/2026 | v1.3.6 | Infra | **Dynamic Route Fix**: Implementación de `generateStaticParams` en `/courses/[slug]` para permitir exportación estática en Cloudflare Pages. |
| 28/03/2026 | v1.3.5 | Infra | **Static Export**: Habilitación de `output: 'export'` en Next.js y cambio de `Output directory` a `out` para Cloudflare Pages. |
| 28/03/2026 | v1.3.4 | Infra | **Migración Worker a Pages**: Corrección de despliegue erróneo como Worker y guía de transición a Cloudflare Pages nativo. |
| 28/03/2026 | v1.3.3 | Infra | **Troubleshooting Domain**: Guía para activar dominios .pages.dev y mejora de logs de URL en Cloudflare. |
| 28/03/2026 | v1.3.2 | Infra | **Fix URL Visibility**: Mejora en el logging de despliegue de Cloudflare para visualizar la URL pública y solución al mensaje 'No URLs enabled'. |
| 28/03/2026 | v1.3.1 | Infra | **Despliegue Exitoso**: Confirmación de build nativo en Cloudflare Pages. URL: [Pendiente - Verificar en panel] |
| 28/03/2026 | v1.3.0 | Infra | **Desacoplamiento Total**: Limpieza definitiva de bindings y desacoplamiento total de OpenNext/Wrangler para despliegue nativo. |
| 28/03/2026 | v1.2.9 | Infra | **Optimización de Build**: Desactivación de telemetría, eliminación de OpenNext y corrección de bucles infinitos en Cloudflare. |
| 28/03/2026 | v1.2.8 | Infra | **Fix Cloudflare Entry-point**: Definición de punto de entrada OpenNext en `wrangler.jsonc` y actualización de script de build. |
| 28/03/2026 | v1.2.7 | Infra | **Fix Cloudflare Binding**: Eliminación de binding circular 'WORKER_SELF_REFERENCE' y restauración de archivos `wrangler.jsonc`. |
| 28/03/2026 | v1.2.6 | Infra | **Fix Despliegue**: Eliminación de trazas de Wrangler, corrección de `next.config.js` y securización de secretos en `render.yaml`. |
| 28/03/2026 | v1.2.5 | Infra | **Simplificación Cloudflare**: Migración a preset nativo de Next.js. Eliminación de OpenNext por inestabilidad en build remoto. |
| 28/03/2026 | v1.2.0 | Infra | **Cloud Deployment**: Configuración de Supabase (DB), Render (API) y Cloudflare Pages (Frontend). |
| 28/03/2026 | v1.1.0 | Migración | **Rebranding total**: Migración de `amauta.ai` a `yachachiy.ai`. Actualización de APIs, base de datos (SQLite), rutas y componentes UI. |
| 28/03/2026 | v1.0.5 | Bug Fix | Solución de `ReferenceError: ExternalLink` y corrección de `asChild prop` en componentes de Shadcn/Base-UI. |
| 28/03/2026 | v1.0.4 | Infra | Migración de PostgreSQL a **SQLite** para facilitar la portabilidad y exploración local. |
| 28/03/2026 | v1.0.0 | Release | Lanzamiento inicial de la plataforma con comparador de cursos y cálculo de ROI. |

---
*Yachachiy.ai - Democratizando el acceso a la información educativa en LatAm.*
