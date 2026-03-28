# Amauta.ai - El "Google Flights" de la Educación en Latinoamérica

Amauta.ai es una plataforma diseñada para centralizar, comparar y optimizar la búsqueda de ofertas educativas en Latinoamérica, comenzando con un enfoque estratégico en el mercado peruano.

## Estado del Proyecto: FASES 1-5 COMPLETADAS ✅

### Fase 1: Piloto de Recolección (UTEC/UPC) - COMPLETADA
- [x] Estructura base del proyecto (FastAPI + Next.js).
- [x] Esquema de PostgreSQL con soporte para geolocalización.
- [x] Scripts de recolección de datos automatizados (Playwright).
- [x] Captura inicial de programas de UTEC y UPC.

### Fase 2: Backend FastAPI y Auditoría de Seguridad - COMPLETADA
- [x] Desarrollo de API asíncrona con SQLAlchemy y Pydantic.
- [x] Implementación de filtrado avanzado (nombre, modalidad, presupuesto).
- [x] Auditoría de seguridad completa y manejo global de excepciones.
- [x] Cobertura de pruebas unitarias e integración al 100%.

### Fase 3: Búsqueda Frontend y Geolocalización - COMPLETADA
- [x] Interfaz de búsqueda dinámica en Next.js 14 con Shadcn/UI.
- [x] Sistema de geolocalización por IP (anonimización obligatoria).
- [x] Cálculo de distancia geodésica (Haversine) para ordenar por cercanía.

### Fase 4: Inteligencia y ROI Académico - COMPLETADA
- [x] Integración de metadatos de salarios esperados por carrera.
- [x] Algoritmo de cálculo de **ROI Académico** (Meses para recuperar la inversión).
- [x] Visualización de indicadores financieros en los detalles del curso.

### Fase 5: Expansión y Comparador - COMPLETADA
- [x] **Módulo de Comparación:** Interfaz para contrastar hasta 3 programas simultáneamente.
- [x] **Captura de Leads:** Sistema de registro para interesados directamente desde la plataforma.
- [x] **Diseño Responsivo:** Optimización total para dispositivos móviles (Mobile-First).

---

## Cómo visualizar e interactuar con Amauta.ai

### Requisitos Previos
- Python 3.10+
- Node.js 18+
- PostgreSQL activo (o Docker para levantar la base de datos)

### 1. Configuración del Backend (API)
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor (desde la raíz)
python api/main.py
```
*La API estará disponible en `http://localhost:8000`*

### 2. Configuración del Frontend (Web)
```bash
cd web
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```
*La interfaz web estará disponible en `http://localhost:3000`*

### Rutas Disponibles en la Web
- `/`: **Buscador Principal**. Filtra cursos por nombre, modalidad y precio. Resultados ordenados por geolocalización automática.
- `/courses/[slug]`: **Detalle del Curso**. Incluye información técnica, mapa de ubicación, cálculo de ROI Académico y formulario de captura de leads.
- `/compare`: **Comparador Educativo**. Permite seleccionar y contrastar diferentes programas para facilitar la toma de decisiones.

---

## Documentación Técnica de la API

### Endpoints Principales

#### `GET /courses`
Lista de cursos con filtros opcionales (`name`, `mode`, `max_price`). Incluye cálculo de distancia basado en la IP del solicitante.

#### `GET /courses/{slug}`
Detalle completo de un programa específico, incluyendo métricas de ROI y coordenadas institucionales.

#### `POST /leads`
Registra el interés de un usuario en un programa específico (Captura de Leads).

### Seguridad y Privacidad
- **Anonimización de IP:** La IP del usuario se anonimiza antes de enviarse a servicios externos de geolocalización.
- **Protección de Datos:** Se utilizan esquemas de Pydantic para asegurar que solo la información necesaria sea expuesta.
- **Validación:** Todas las entradas son validadas estrictamente para prevenir inyecciones y ataques comunes.

---
*Amauta.ai - Democratizando el acceso a la información educativa en LatAm.*
