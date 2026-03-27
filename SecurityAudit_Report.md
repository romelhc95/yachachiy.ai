# Reporte de Auditoría de Seguridad de Amauta.ai v1.0
**Fecha:** 27-03-2026
**Auditor:** @gemini\agents\security-auditor (Simulado por Gemini CLI)

## Resumen Ejecutivo
Esta auditoría evaluó el entorno Docker, la configuración de PostgreSQL y los scripts de la aplicación del proyecto Amauta.ai. Aunque la lógica de la aplicación utiliza consultas parametrizadas para prevenir la inyección SQL, se identificaron varias vulnerabilidades a nivel de infraestructura que podrían comprometer la integridad y confidencialidad de los datos.

## 1. Entorno e Infraestructura (Docker)
| ID | Hallazgo | Severidad | Recomendación |
|----|---------|----------|----------------|
| S1.1 | **Credenciales Hardcodeadas** | Alta | Mover `POSTGRES_PASSWORD` a un archivo `.env` y usar Docker Secrets. Evitar hardcodear en `scripts/*.py`. |
| S1.2 | **Puerto de BD Expuesto** | Media | Eliminar el mapeo de puertos `5432:5432` en `docker-compose.yml` a menos que se requiera acceso externo estrictamente. |
| S1.3 | **Ejecución como Usuario Root** | Media | Actualizar el `Dockerfile` para crear y usar un usuario que no sea root (ej. `amauta_user`). |
| S1.4 | **Paquetes Desactualizados** | Baja | Implementar un paso para escanear vulnerabilidades en la imagen base `python:3.11-slim`. |

## 2. Seguridad de la Base de Datos (PostgreSQL)
| ID | Hallazgo | Severidad | Recomendación |
|----|---------|----------|----------------|
| S2.1 | **Conexiones en Texto Plano** | Media | Configurar PostgreSQL para requerir SSL/TLS en todas las conexiones. |
| S2.2 | **Contraseña Débil** | Alta | Cambiar la contraseña predeterminada `password_amauta` por un secreto fuerte generado aleatoriamente. |
| S2.3 | **Uso del Esquema Public** | Baja | Considerar mover las tablas de la aplicación a un esquema dedicado en lugar de `public`. |

## 3. Código de la Aplicación (Scripts de Python)
- **Inyección SQL:** No se encontraron vulnerabilidades. Todas las interacciones con la base de datos en `harvester.py`, `discover_courses.py` y `ai_parser.py` utilizan consultas parametrizadas.
- **Manejo de Errores:** Se presentan bloques try/except básicos, pero podrían mejorarse para evitar la filtración de rutas del sistema o la estructura de la BD en los registros (logs) de producción.

## 4. Plan de Remediación (Fase 1)
1. **Gestión de Credenciales:** Crear un archivo `.env` y actualizar `docker-compose.yml` para usarlo.
2. **Endurecimiento de Docker (Hardening):** Añadir `USER` al `Dockerfile` y eliminar los puertos expuestos.
3. **Endurecimiento de la Base de Datos:** Actualizar `db/init.sql` con permisos más restrictivos si se añaden más usuarios posteriormente.

## Conclusión
La configuración actual es adecuada para un piloto local pero requiere endurecimiento antes de cualquier despliegue público. El enfoque principal debe estar en la gestión de credenciales y la seguridad de los contenedores Docker.
