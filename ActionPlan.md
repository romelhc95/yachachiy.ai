# Action Plan: Sprint 1 - Harvester for Amauta.ai

## Goal
Build the PostgreSQL foundation and implement automated data ingestion for Peruvian universities (UTEC and UPC as pilots).

## 1. Data Architecture (Coordination with @architect)
- **Database**: PostgreSQL 16.
- **Schema**:
    - `institutions`: Focus on geolocation and metadata.
    - `courses`: Focus on pricing (PEN) and delivery modes.
- **File**: `db/init.sql`.

## 2. Infrastructure
- **Containerization**: Docker and Docker Compose.
- **Services**:
    - `db`: PostgreSQL.
    - `harvester`: Python + Playwright for scraping and parsing.

## 3. Data Ingestion (Coordination with @data-harvester)
- **Scraper**: Python script using `playwright`.
- **Targets**:
    - UTEC (Universidad de Ingeniería y Tecnología).
    - UPC (Universidad Peruana de Ciencias Aplicadas).
- **Output**: Raw HTML/JSON to be passed to the parser.

## 4. Standardization (Coordination with @ai-parser)
- **Format**: JSON.
- **Fields**:
    - `name`: Course/Program name.
    - `price`: Standardized to PEN (float).
    - `mode`: Presencial, Híbrido, or Remoto.
    - `address`: Physical location or "Online".

## 5. Quality Assurance (Coordination with @tdd-lead)
- **Framework**: `pytest`.
- **Initial Tests**:
    - Check for duplicate records (Upsert logic).
    - Validate that prices are non-null and positive.

## 6. Action Steps
1. Create `db/init.sql` with the specified schema.
2. Create `docker-compose.yml` and `Dockerfile`.
3. Implement `scripts/harvester.py` (Pilot for UTEC/UPC).
4. Define `parser/schema.json` and `parser/logic.py` (Integration with AI Parser).
5. Create `tests/` directory with initial test cases.
