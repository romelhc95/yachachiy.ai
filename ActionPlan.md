# Plan de Acción: Fase 1 - Harvester para Amauta.ai

## Objetivo
Construir la base de PostgreSQL e implementar la ingesta automatizada de datos para universidades peruanas (UTEC y UPC como pilotos).

## 1. Arquitectura de Datos (Coordinación con @architect)
- **Base de Datos**: PostgreSQL 16.
- **Esquema**:
    - `institutions`: Centrado en geolocalización y metadatos.
    - `courses`: Centrado en precios (PEN) y modalidades de dictado.
- **Archivo**: `db/init.sql`.

## 2. Infraestructura
- **Contenerización**: Docker y Docker Compose.
- **Servicios**:
    - `db`: PostgreSQL.
    - `harvester`: Python + Playwright para scraping y parsing.

## 3. Ingesta de Datos (Coordinación con @data-harvester)
- **Scraper**: Script de Python usando `playwright`.
- **Objetivos**:
    - UTEC (Universidad de Ingeniería y Tecnología).
    - UPC (Universidad Peruana de Ciencias Aplicadas).
- **Salida**: HTML/JSON raw para ser entregado al parser.

## 4. Estandarización (Coordinación con @ai-parser)
- **Formato**: JSON.
- **Campos**:
    - `name`: Nombre del curso/programa.
    - `price`: Estandarizado a PEN (float).
    - `mode`: Presencial, Híbrido o Remoto.
    - `address`: Ubicación física u "Online".

## 5. Aseguramiento de la Calidad (Coordinación con @tdd-lead)
- **Framework**: `pytest`.
- **Pruebas Iniciales**:
    - Verificar registros duplicados (Lógica de Upsert).
    - Validar que los precios no sean nulos y sean positivos.

## 6. Pasos a Seguir
1. Crear `db/init.sql` con el esquema especificado.
2. Crear `docker-compose.yml` y `Dockerfile`.
3. Implementar `scripts/harvester.py` (Piloto para UTEC/UPC).
4. Definir `parser/schema.json` y `parser/logic.py` (Integración con AI Parser).
5. Crear el directorio `tests/` con los casos de prueba iniciales.
