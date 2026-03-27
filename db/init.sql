-- Initial PostgreSQL Schema for Amauta.ai
-- Created for Sprint 1: Harvester Pilot (UTEC/UPC)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: institutions
CREATE TABLE IF NOT EXISTS institutions (
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
CREATE INDEX idx_institutions_slug ON institutions(slug);
CREATE INDEX idx_courses_price ON courses(price_pen);
CREATE INDEX idx_courses_mode ON courses(mode);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON institutions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Seed Pilot Institutions
INSERT INTO institutions (name, slug, address) VALUES 
('Universidad de Ingeniería y Tecnología', 'utec', 'Jr. Medrano Silva 165, Barranco, Lima'),
('Universidad Peruana de Ciencias Aplicadas', 'upc', 'Prolongación Primavera 2390, Monterrico, Lima')
ON CONFLICT (slug) DO NOTHING;
