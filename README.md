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

## 📜 Control de Versionamiento y Cambios
Registro de hitos y modificaciones significativas en el proyecto:

| Fecha | Versión | Tipo | Descripción de Cambios |
| :--- | :--- | :--- | :--- |
| 28/03/2026 | v1.1.0 | Migración | **Rebranding total**: Migración de `amauta.ai` a `yachachiy.ai`. Actualización de APIs, base de datos (SQLite), rutas y componentes UI. |
| 28/03/2026 | v1.0.5 | Bug Fix | Solución de `ReferenceError: ExternalLink` y corrección de `asChild prop` en componentes de Shadcn/Base-UI. |
| 28/03/2026 | v1.0.4 | Infra | Migración de PostgreSQL a **SQLite** para facilitar la portabilidad y exploración local. |
| 28/03/2026 | v1.0.0 | Release | Lanzamiento inicial de la plataforma con comparador de cursos y cálculo de ROI. |

---
*Yachachiy.ai - Democratizando el acceso a la información educativa en LatAm.*
