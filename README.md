# Amauta.ai - El Google Flights de Educación en LatAm

Amauta.ai es una plataforma diseñada para centralizar y comparar ofertas educativas en Latinoamérica, comenzando por el mercado peruano.

## Fase 1: Piloto de Recolección (UTEC/UPC) - COMPLETADA
- [x] Estructura base del proyecto.
- [x] Esquema inicial de PostgreSQL orientado a geolocalización.
- [x] Scripts de recolección de datos iniciales.
- [x] **8 programas de DATA capturados** (Piloto UTEC & UPC).

## Fase 2: Backend FastAPI y Auditoría de Seguridad - COMPLETADA
- [x] **Núcleo del Backend:** Aplicación FastAPI en `/api` con ORM SQLAlchemy.
- [x] **API Segura:** Implementación de `GET /courses` con filtrado (nombre, modalidad, precio máximo).
- [x] **Auditoría de Seguridad:** Validación estandarizada con Pydantic y manejo global de excepciones (sin trazas de error).
- [x] **Pruebas Automatizadas:** Cobertura de pruebas del 100% para los endpoints de la API con Pytest (`tests/test_fase2.py`).
- [x] **Inicio del Frontend:** Next.js 14 configurado en `/web` con Tailwind CSS y Shadcn/UI.

## Fase 3: Búsqueda Frontend y Lógica de Geolocalización - COMPLETADA
- [x] **Geolocalización:** Implementada lógica de cálculo de distancia Haversine (geodésica) basada en IP.
- [x] **Privacidad:** Anonimización de IPs (máscara de último octeto) antes de geolocalización externa.
- [x] **Búsqueda Frontend:** Buscador interactivo en Next.js 14 con tarjetas minimalistas de Shadcn/UI.
- [x] **Ordenación:** Resultados ordenados automáticamente por cercanía al usuario.

### Flujo de Geolocalización
1. El Frontend solicita `GET /courses`.
2. El Backend identifica la IP del cliente (`request.client.host`).
3. La IP es anonimizada (ej. `190.235.154.12` -> `190.235.154.0`).
4. Se consultan las coordenadas (lat, lon) mediante `ip-api.com`.
5. Se calcula la distancia entre el usuario y cada institución usando la fórmula Haversine (`geopy`).
6. Los resultados se inyectan con el campo `distance_km` y se ordenan de menor a mayor distancia.
7. Las coordenadas exactas de las instituciones se filtran mediante Pydantic para no exponer datos sensibles.

## Documentación Técnica de la API

### URL Base
`http://localhost:8000` (predeterminada para desarrollo)

### Endpoints

#### 1. Buscar Cursos
`GET /courses`

Devuelve una lista de cursos con filtros opcionales.

**Parámetros de Consulta:**
| Parámetro | Tipo | Descripción |
| :--- | :--- | :--- |
| `name` | string | Coincidencia parcial (insensible a mayúsculas) para el nombre del curso. |
| `mode` | string | Filtrar por modalidad: `Presencial`, `Híbrido`, `Remoto`. |
| `max_price` | decimal | Precio máximo en PEN. |

**Ejemplo de Solicitud:**
`GET /courses?name=Ciencia&mode=Remoto&max_price=1000`

**Ejemplo de Respuesta:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "institution_id": "6eb31464-a690-4963-9562-b9116a49591e",
    "institution_name": "UPN",
    "name": "Ingeniería en Ciencia de Datos",
    "slug": "ingenieria-en-ciencia-de-datos",
    "price_pen": 0.0,
    "mode": "Híbrido",
    "address": "Sede Breña/Los Olivos, Lima",
    "duration": "10 ciclos",
    "url": "https://www.upn.edu.pe/...",
    "last_scraped_at": "2026-03-27T10:00:00Z",
    "created_at": "2026-03-27T10:00:00Z",
    "updated_at": "2026-03-27T10:00:00Z"
  }
]
```

### Seguridad y Manejo de Errores
- **Prevención de Inyección SQL:** Todas las consultas utilizan el ORM SQLAlchemy con entradas parametrizadas.
- **Validación de Datos:** Los esquemas de Pydantic imponen tipado estricto y restricciones en todas las entradas/salidas de la API.
- **Privacidad de Errores:** Un manejador de excepciones global captura todas las excepciones no controladas y devuelve un mensaje 500 genérico, evitando la filtración de información sensible del sistema o trazas de la pila (stack traces).

## Arquitectura de Base de Datos
Estado actual: Operativa en Docker con PostgreSQL 16.
- [x] **Instituciones:** UTEC y UPC inicializadas.
- [x] **Cursos:** 8 registros activos con metadatos de modalidad y geolocalización.

### Esquema SQL (Fase 1.1)
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla: institutions
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    website_url TEXT,
    location_lat DECIMAL(10, 8),
    location_long DECIMAL(11, 8),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: courses
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255),
    price_pen DECIMAL(12, 2),
    mode VARCHAR(50),
    address TEXT,
    duration VARCHAR(100),
    url TEXT,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---
*Documentación generada automáticamente por el servidor MCP de GitHub - Amauta.ai Architect*
