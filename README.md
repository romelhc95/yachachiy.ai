# Amauta.ai - El Google Flights de Educación en LatAm

Amauta.ai es una plataforma diseñada para centralizar y comparar ofertas educativas en Latinoamérica, comenzando por el mercado peruano.

## Sprint 1: Harvester Pilot (UTEC/UPC)
- [x] Estructura base del proyecto.
- [x] Esquema inicial de PostgreSQL orientado a geolocalización.
- [x] Scripts de recolección de datos iniciales.

## Arquitectura de Base de Datos
Este esquema define las entidades principales para instituciones y cursos.

### Esquema SQL (Sprint 1)
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: institutions
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

-- Table: courses
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

(Más detalles a ser agregados por @architect)
