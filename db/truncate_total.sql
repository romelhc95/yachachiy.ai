-- Script SQL para vaciar las tablas 'courses', 'institutions' y 'leads'.
-- Incluye RESTART IDENTITY para reiniciar los contadores de las columnas autoincrementales.
-- Incluye CASCADE para manejar las dependencias de claves foráneas.

TRUNCATE TABLE courses, institutions, leads RESTART IDENTITY CASCADE;
