-- Initial PostgreSQL Schema for Yachachiy.ai
-- Created for Fase 1: Harvester Pilot (UTEC/UPC)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum Types for Institutions
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'institution_type') THEN
        CREATE TYPE institution_type AS ENUM ('Univ', 'Inst');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'institution_status') THEN
        CREATE TYPE institution_status AS ENUM ('Activa', 'Inactiva');
    END IF;
END $$;

-- Compatibilidad con enums de instituciones
ALTER TYPE institution_type ADD VALUE IF NOT EXISTS 'Univ';
ALTER TYPE institution_type ADD VALUE IF NOT EXISTS 'Inst';

ALTER TYPE institution_status ADD VALUE IF NOT EXISTS 'Activa';
ALTER TYPE institution_status ADD VALUE IF NOT EXISTS 'Inactiva';

-- Table: institutions
CREATE TABLE IF NOT EXISTS institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    website_url TEXT,
    official_website TEXT,
    type institution_type DEFAULT 'Univ',
    status institution_status DEFAULT 'Activa',
    region VARCHAR(100),
    location_lat DECIMAL(10, 8),
    location_long DECIMAL(11, 8),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Asegurar compatibilidad para añadir columnas si la tabla ya existía
ALTER TABLE institutions ADD COLUMN IF NOT EXISTS official_website TEXT;
ALTER TABLE institutions ADD COLUMN IF NOT EXISTS type institution_type DEFAULT 'Univ';
ALTER TABLE institutions ADD COLUMN IF NOT EXISTS status institution_status DEFAULT 'Activa';
ALTER TABLE institutions ADD COLUMN IF NOT EXISTS region VARCHAR(100);

-- Table: courses
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255),
    price_pen DECIMAL(12, 2) CHECK (price_pen >= 0),
    mode VARCHAR(50) CHECK (mode IN ('Presencial', 'Híbrido', 'Remoto')),
    address TEXT,
    duration VARCHAR(100),
    url TEXT,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(institution_id, name, slug) -- To prevent duplicates from the same institution
);

-- Indices for performance and search
CREATE INDEX IF NOT EXISTS idx_institutions_slug ON institutions(slug);
CREATE INDEX IF NOT EXISTS idx_courses_price ON courses(price_pen);
CREATE INDEX IF NOT EXISTS idx_courses_mode ON courses(mode);
CREATE INDEX IF NOT EXISTS idx_institutions_region ON institutions(region);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_institutions_updated_at') THEN
        CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON institutions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_courses_updated_at') THEN
        CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    END IF;
END $$;

-- Seed Pilot Institutions
INSERT INTO institutions (name, slug, address, official_website, type, status, region) VALUES 
('Universidad de Ingeniería y Tecnología', 'utec', 'Jr. Medrano Silva 165, Barranco, Lima', 'https://utec.edu.pe', 'Univ', 'Activa', 'Lima'),
('Universidad Peruana de Ciencias Aplicadas', 'upc', 'Prolongación Primavera 2390, Monterrico, Lima', 'https://upc.edu.pe', 'Univ', 'Activa', 'Lima')
ON CONFLICT (slug) DO UPDATE SET 
    official_website = EXCLUDED.official_website,
    type = EXCLUDED.type,
    status = EXCLUDED.status,
    region = EXCLUDED.region;
