
-- 1. Ensure Enums exist
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lead_type') THEN
        CREATE TYPE lead_type AS ENUM ('info', 'recommendation');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lead_status') THEN
        CREATE TYPE lead_status AS ENUM ('pending', 'contacted', 'resolved');
    END IF;
END $$;

-- 2. Add missing values to existing enums (just in case)
ALTER TYPE lead_type ADD VALUE IF NOT EXISTS 'info';
ALTER TYPE lead_type ADD VALUE IF NOT EXISTS 'recommendation';
ALTER TYPE lead_status ADD VALUE IF NOT EXISTS 'pending';
ALTER TYPE lead_status ADD VALUE IF NOT EXISTS 'contacted';
ALTER TYPE lead_status ADD VALUE IF NOT EXISTS 'resolved';

-- 3. Update Leads Table structure
ALTER TABLE leads 
    ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS last_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS email VARCHAR(255),
    ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(50),
    ADD COLUMN IF NOT EXISTS type lead_type,
    ADD COLUMN IF NOT EXISTS course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS area_interest VARCHAR(255),
    ADD COLUMN IF NOT EXISTS budget DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS modality VARCHAR(100),
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS status lead_status DEFAULT 'pending';

-- 4. Set defaults and NOT NULL for mandatory fields (after ensuring they exist)
UPDATE leads SET first_name = '' WHERE first_name IS NULL;
UPDATE leads SET last_name = '' WHERE last_name IS NULL;
UPDATE leads SET email = '' WHERE email IS NULL;
UPDATE leads SET whatsapp = '' WHERE whatsapp IS NULL;
UPDATE leads SET type = 'info' WHERE type IS NULL;

ALTER TABLE leads 
    ALTER COLUMN first_name SET NOT NULL,
    ALTER COLUMN last_name SET NOT NULL,
    ALTER COLUMN email SET NOT NULL,
    ALTER COLUMN whatsapp SET NOT NULL,
    ALTER COLUMN type SET NOT NULL;
