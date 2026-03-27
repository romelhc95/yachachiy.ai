# Amauta.ai Security Audit Report v1.0
**Date:** 2026-03-27
**Auditor:** @gemini\agents\security-auditor (Simulated by Gemini CLI)

## Executive Summary
This audit evaluated the Docker environment, PostgreSQL configuration, and application scripts of the Amauta.ai project. While the application logic uses parameterized queries to prevent SQL injection, several infrastructure-level vulnerabilities were identified that could compromise data integrity and confidentiality.

## 1. Environment & Infrastructure (Docker)
| ID | Finding | Severity | Recommendation |
|----|---------|----------|----------------|
| S1.1 | **Hardcoded Credentials** | High | Move `POSTGRES_PASSWORD` to a `.env` file and use Docker Secrets. Avoid hardcoding in `scripts/*.py`. |
| S1.2 | **Exposed DB Port** | Medium | Remove the `5432:5432` port mapping in `docker-compose.yml` unless external access is strictly required. |
| S1.3 | **Root User Execution** | Medium | Update `Dockerfile` to create and use a non-root user (e.g., `amauta_user`). |
| S1.4 | **Outdated Packages** | Low | Implement a step to scan for vulnerabilities in the `python:3.11-slim` base image. |

## 2. Database Security (PostgreSQL)
| ID | Finding | Severity | Recommendation |
|----|---------|----------|----------------|
| S2.1 | **Plaintext Connections** | Medium | Configure PostgreSQL to require SSL/TLS for all connections. |
| S2.2 | **Weak Password** | High | Change the default `password_amauta` to a strong, randomly generated secret. |
| S2.3 | **Public Schema Usage** | Low | Consider moving application tables to a dedicated schema instead of `public`. |

## 3. Application Code (Python Scripts)
- **SQL Injection:** No vulnerabilities found. All database interactions in `harvester.py`, `discover_courses.py`, and `ai_parser.py` use parameterized queries.
- **Error Handling:** Basic try/except blocks are present, but could be enhanced to avoid leaking system paths or DB structure in production logs.

## 4. Remediation Plan (Phase 1)
1. **Credentials Management:** Create a `.env` file and update `docker-compose.yml` to use it.
2. **Docker Hardening:** Add `USER` to `Dockerfile` and remove exposed ports.
3. **Database Hardening:** Update `db/init.sql` with more restrictive permissions if multiple users are added later.

## Conclusion
The current setup is suitable for a local pilot but requires hardening before any public deployment. The primary focus should be on credential management and Docker container security.
