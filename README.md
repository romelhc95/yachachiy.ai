# Yachachiy.ai - Democratizando la Educación en el Perú 🇵🇪

Yachachiy.ai es una plataforma impulsada por IA diseñada para centralizar, comparar y optimizar la búsqueda de educación superior en el Perú. Utiliza un stack moderno serverless para garantizar alta disponibilidad y seguridad en el manejo de datos académicos.

## 🏛️ Nueva Arquitectura (2025)

El sistema ha evolucionado de una arquitectura monolítica a un modelo **Full Serverless** de alto rendimiento:

1.  **Frontend:** Next.js 15 (App Router) desplegado en **Cloudflare Pages**.
2.  **Data Layer (Bypass de Backend):** El cliente se comunica directamente con la API REST de **Supabase** (PostgreSQL) mediante una capa de seguridad endurecida.
3.  **Procesamiento de IA:** Scripts especializados (`ai_parser.py`, `harvester.py`) que procesan datos de instituciones peruanas y realizan el UPSERT hacia la base de datos centralizada.

## 🛠️ Stack Tecnológico

-   **Framework:** [Next.js](https://nextjs.org/) (React 18+)
-   **Estilos:** [Tailwind CSS](https://tailwindcss.com/)
-   **Componentes UI:** [Shadcn/UI](https://ui.shadcn.com/)
-   **Iconografía:** [Lucide React](https://lucide.dev/)
-   **Base de Datos & Auth:** [Supabase](https://supabase.com/) (PostgreSQL)
-   **Automatización:** Python 3.11+ (Requests, BeautifulSoup, Playwright)

## 🛡️ Estándares de Seguridad

Para garantizar la integridad y privacidad de los datos sin un backend intermedio, se han implementado:

-   **Row Level Security (RLS):** Las tablas en Supabase tienen políticas estrictas.
    -   `courses`: Lectura pública (`SELECT`), inserción restringida.
    -   `leads`: Inserción pública (`INSERT`), lectura prohibida para el rol anónimo (`SELECT` retorna vacío).
-   **Anon Key Hardening:** La clave `anon_key` está configurada para permitir solo las operaciones de negocio necesarias.
-   **Flujo Hermético:** El flujo `Cursos -> UI -> Leads` garantiza que la información de contacto de los usuarios sea unidireccional (sólo llega a la base de datos y no es accesible desde el cliente).

## 🚀 Guía de Desarrollo

### Requisitos Previos
- Node.js 18+
- Python 3.11+ (para scrapers y procesamiento)

### Local vs Producción
1.  **Entorno Local:**
    -   Clonar el repositorio.
    -   Instalar dependencias: `cd web && npm install`.
    -   Configurar variables en `.env.local` (Supabase URL y Anon Key).
    -   Ejecutar: `npm run dev`.
2.  **Producción:**
    -   Despliegue automático vía GitHub Actions a **Cloudflare Pages**.
    -   La base de datos reside en **Supabase Cloud (Región us-east-1)**.

## 📊 Estado del Mapa Institucional (Fase 2)

-   **Instituciones Mapeadas:** 36 (Principales universidades e institutos del Perú).
-   **Cursos Piloto Ingestados:** 19 (Enfoque en alta demanda laboral).
-   **Puntos de Datos Capturados:** Precio Real, ROI Proyectado, Temario, Ubicación, Modalidad y Duración.

---
© 2026 Yachachiy.ai - Todos los derechos reservados.
