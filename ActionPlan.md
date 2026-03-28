# Plan de Acción: Fase 1 - Recolector para Amauta.ai

## Objetivo
Construir la base de PostgreSQL e implementar la ingesta automatizada de datos para universidades peruanas (UTEC y UPC como pilotos).

## 1. Arquitectura de Datos (Coordinación con el Arquitecto)
- **Base de Datos**: PostgreSQL 16.
- **Esquema**:
    - `institutions`: Centrado en geolocalización y metadatos.
    - `courses`: Centrado en precios (PEN) y modalidades de dictado.
- **Archivo**: `db/init.sql`.

## 2. Infraestructura
- **Contenerización**: Docker y Docker Compose.
- **Servicios**:
    - `db`: PostgreSQL.
    - `recolector`: Python + Playwright para extracción y procesamiento.

## 3. Ingesta de Datos (Coordinación con el Recolector de Datos)
- **Extractor**: Script de Python usando `playwright`.
- **Objetivos**:
    - UTEC (Universidad de Ingeniería y Tecnología).
    - UPC (Universidad Peruana de Ciencias Aplicadas).
- **Salida**: HTML/JSON en bruto para ser entregado al procesador.

## 4. Estandarización (Coordinación con el Procesador de IA)
- **Formato**: JSON.
- **Campos**:
    - `name`: Nombre del curso/programa.
    - `price`: Estandarizado a PEN (decimal).
    - `mode`: Presencial, Híbrido o Remoto.
    - `address`: Ubicación física u "Online".

## 5. Aseguramiento de la Calidad (Coordinación con el Líder de TDD)
- **Marco de trabajo**: `pytest`.
- **Pruebas Iniciales**:
    - Verificar registros duplicados (Lógica de Actualización/Inserción).
    - Validar que los precios no sean nulos y sean positivos.

## 6. Pasos a Seguir
1. Crear `db/init.sql` con el esquema especificado.
2. Crear `docker-compose.yml` y `Dockerfile`.
3. Implementar `scripts/harvester.py` (Piloto para UTEC/UPC).
4. Definir `parser/schema.json` y `parser/logic.py` (Integración con el Procesador de IA).
5. Crear el directorio `tests/` con los casos de prueba iniciales.
