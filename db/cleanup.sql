-- db/cleanup.sql
-- Script robusto para limpiar las tablas de la base de datos Supabase (PostgreSQL)
-- de cara a un nuevo proceso de seeding limpio.

DO $$
BEGIN
    -- 1. Limpiar tabla 'institutions' y sus dependencias (CASCADE)
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'institutions') THEN
        EXECUTE 'TRUNCATE TABLE institutions RESTART IDENTITY CASCADE;';
    END IF;

    -- 2. Limpiar tabla 'courses' y sus dependencias (CASCADE)
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'courses') THEN
        EXECUTE 'TRUNCATE TABLE courses RESTART IDENTITY CASCADE;';
    END IF;

    -- 3. Limpiar tabla 'locations' por si existe como tabla auxiliar de geolocalización
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'locations') THEN
        EXECUTE 'TRUNCATE TABLE locations RESTART IDENTITY CASCADE;';
    END IF;
END $$;
