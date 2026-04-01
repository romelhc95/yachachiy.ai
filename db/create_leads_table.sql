-- SQL for creating leads table and updating institutions
-- Created by @architect for Yachachiy.ai

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Enum Types
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lead_type') THEN
        CREATE TYPE lead_type AS ENUM ('info', 'recommendation');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lead_status') THEN
        CREATE TYPE lead_status AS ENUM ('pending', 'contacted', 'resolved');
    END IF;
END $$;

-- 1.5 Compatibilidad con tabla existente: Agregar nuevos valores al enum si la base de datos ya tenía otros
ALTER TYPE lead_type ADD VALUE IF NOT EXISTS 'info';
ALTER TYPE lead_type ADD VALUE IF NOT EXISTS 'recommendation';

ALTER TYPE lead_status ADD VALUE IF NOT EXISTS 'pending';
ALTER TYPE lead_status ADD VALUE IF NOT EXISTS 'contacted';
ALTER TYPE lead_status ADD VALUE IF NOT EXISTS 'resolved';

-- 2. Create Leads Table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    whatsapp VARCHAR(50) NOT NULL,
    type lead_type NOT NULL,
    course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
    area_interest VARCHAR(255),
    budget DECIMAL(12, 2),
    modality VARCHAR(100),
    description TEXT,
    status lead_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Indices
CREATE INDEX IF NOT EXISTS idx_leads_course_id ON leads(course_id);
CREATE INDEX IF NOT EXISTS idx_leads_type ON leads(type);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

-- 4. RLS Policy for leads insertion
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir inserción pública de leads" ON public.leads;
CREATE POLICY "Permitir inserción pública de leads" ON public.leads 
FOR INSERT 
TO anon 
WITH CHECK (true);
