
import asyncio
import os
import sys
import re
import json
import uuid
from datetime import datetime
from decimal import Decimal
from playwright.async_api import async_playwright
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurar DATABASE_URL para MySQL local 3307
os.environ["DATABASE_URL"] = "mysql+pymysql://root:@localhost:3307/yachachiy"

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import Institution, Course

# Configuration
MAX_PROGRAMS = 40
TIMEOUT = 60000
UNI_SLUG = "uni"
UNI_NAME = "Universidad Nacional de Ingeniería (UNI)"
UNI_BASE_URL = "https://posgrado.uni.edu.pe"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def standardize_mode(text):
    text = text.lower()
    if any(kw in text for kw in ['remoto', 'virtual', 'online', 'a distancia', 'e-learning']):
        return 'Remoto'
    if any(kw in text for kw in ['hibrido', 'híbrido', 'semipresencial', 'blended']):
        return 'Híbrido'
    return 'Presencial'

def extract_price(text):
    text_lower = text.lower()
    if any(kw in text_lower for kw in ['gratis', 'sin costo', 'free', 'beca 100%']):
        return 0.0
    
    # S/ 1,500.00 or S/. 1500 or PEN 2000 or USD 500
    price_match = re.search(r'(?:S/|S/\.|PEN|USD|\$)\s*([\d,.]+)', text)
    if price_match:
        price_str = price_match.group(1).replace(',', '')
        try:
            val = float(price_str)
            if val > 100: # Threshold for real courses
                return val
        except:
            pass
    return None

def is_valid_course(name, text, url):
    """Rigorous validation for @tdd-lead"""
    # 1. Must have a reasonable name length
    if len(name) < 10:
        return False, "Nombre muy corto"
    
    # 2. Must not be a news item, blog, or general page
    invalid_keywords = ['noticia', 'comunicado', 'evento', 'bienvenida', 'mensaje del rector', 'galería', 'galeria', 'contacto', 'nosotros', 'acreditación', 'biblioteca']
    if any(kw in name.lower() for kw in invalid_keywords):
        return False, "Palabra clave inválida"
    
    # 3. Must be an academic program
    academic_keywords = ['maestría', 'maestria', 'doctorado', 'diplomado', 'curso', 'taller', 'especialidad', 'programa', 'mención', 'mencion', 'ingeniería', 'ingenieria', 'formación']
    if not any(kw in name.lower() for kw in academic_keywords):
        return False, "No parece programa académico"

    # 4. Content must be substantial
    if len(text) < 200:
        return False, f"Contenido insuficiente ({len(text)} chars)"

    # 5. Must have a valid URL
    if not url or not url.startswith('http'):
        return False, "URL inválida"
        
    return True, ""

async def scrape_uni():
    print(f"=== [Director] Iniciando Línea de Ensamblaje para UNI ===")
    
    # Obtener ID de UNI
    db = SessionLocal()
    uni_inst = db.query(Institution).filter(Institution.slug == UNI_SLUG).first()
    if not uni_inst:
        print("[ERROR] Institución UNI no encontrada en la DB.")
        db.close()
        return
    
    UNI_ID = uni_inst.id
    print(f"[Director] UNI Institution ID: {UNI_ID}")
    db.close()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Phase 1: Discovery
        print(f"[data-harvester] Navegando a {UNI_BASE_URL}...")
        try:
            await page.goto(UNI_BASE_URL, timeout=TIMEOUT, wait_until="networkidle")
            await asyncio.sleep(3)
            
            # Extract program links from the main page
            links = await page.query_selector_all("a")
            
            potential_links = []
            seen_potential_urls = set()
            for link in links:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                text = text.strip()
                
                if href and len(text) > 10:
                    if href.startswith('/'):
                        href = UNI_BASE_URL.rstrip('/') + href
                    
                    # Filtrar enlaces que no sean de UNI o que parezcan irrelevantes
                    if (UNI_BASE_URL in href or "uni.edu.pe" in href) and href not in seen_potential_urls:
                        if any(kw in text.lower() for kw in ['maestría', 'maestria', 'doctorado', 'diplomado', 'curso', 'taller', 'especialidad']):
                            potential_links.append((text, href))
                            seen_potential_urls.add(href)
            
            # También intentar navegar a secciones de programas si están disponibles
            print(f"[data-harvester] {len(potential_links)} enlaces iniciales encontrados.")
            
            # Phase 2 & 3: Extraction & Validation
            valid_courses = []
            seen_urls = set()
            
            for name, url in potential_links:
                if url in seen_urls: continue
                if len(valid_courses) >= MAX_PROGRAMS: break
                
                print(f"[data-harvester] Visitando: {name} ({url})")
                try:
                    await page.goto(url, timeout=TIMEOUT, wait_until="domcontentloaded")
                    await asyncio.sleep(2)
                    
                    # Capturar texto de todo el cuerpo
                    raw_text = await page.inner_text("body")
                    
                    # Validation (@tdd-lead)
                    is_valid, reason = is_valid_course(name, raw_text, url)
                    if not is_valid:
                        print(f"  [tdd-lead] Registro descartado: {reason}")
                        continue
                    
                    # Parsing (@ai-parser)
                    price = extract_price(raw_text)
                    mode = standardize_mode(raw_text)
                    
                    # Detailed fields
                    description = ""
                    # Intento de extracción de descripción
                    desc_match = re.search(r'(?:Presentación|Descripción|Sobre el programa|Resumen|Introducción):(.*?)(?:\n\n|\n[A-Z])', raw_text, re.DOTALL | re.IGNORECASE)
                    if desc_match:
                        description = desc_match.group(1).strip()
                    else:
                        description = raw_text[:500].replace('\n', ' ').strip()
                    
                    duration = "No especificado"
                    dur_match = re.search(r'(?:Duración|Tiempo|Periodo|Meses|Semanas|Horas):(.*?)(?:\n|$)', raw_text, re.IGNORECASE)
                    if dur_match: duration = dur_match.group(1).strip()
                    
                    target = "Público en general"
                    target_match = re.search(r'(?:Dirigido a|Perfil del postulante|Público objetivo|Requisitos):(.*?)(?:\n|$)', raw_text, re.IGNORECASE)
                    if target_match: target = target_match.group(1).strip()
                    
                    syllabus = "Estructura curricular detallada en sitio oficial."
                    syllabus_match = re.search(r'(?:Plan de estudios|Malla curricular|Contenido|Temario|Estructura)(.*?)(?:\n\n|\n[A-Z])', raw_text, re.DOTALL | re.IGNORECASE)
                    if syllabus_match: syllabus = syllabus_match.group(1).strip()
                    
                    category = 'Curso'
                    if 'maestría' in name.lower() or 'maestria' in name.lower(): category = 'Maestría'
                    elif 'doctorado' in name.lower(): category = 'Doctorado'
                    elif 'diplomado' in name.lower(): category = 'Diplomado'
                    elif 'especialidad' in name.lower(): category = 'Especialidad'
                    
                    valid_courses.append({
                        "institution_id": UNI_ID,
                        "name": name,
                        "slug": slugify(f"{name}-{UNI_SLUG}"),
                        "category": category,
                        "price_pen": price,
                        "mode": mode,
                        "address": "Lima, Rímac",
                        "url": url,
                        "description": description[:1000],
                        "duration": duration[:100],
                        "target_audience": target[:500],
                        "syllabus": syllabus[:2000],
                        "last_scraped_at": datetime.now()
                    })
                    seen_urls.add(url)
                    print(f"  [ai-parser] Mapeo completo: {name} (Inversión: {price if price else 'null'})")
                    
                except Exception as e:
                    print(f"  [ERROR] Al procesar {url}: {e}")
            
            # Phase 4: Upsert (@backend-core)
            print(f"[backend-core] Realizando UPSERT de {len(valid_courses)} cursos en MySQL (Port 3307)...")
            new_c, upd_c = upsert_to_db(valid_courses)
            
            print(f"\n=== REPORTE FINAL YACHACHIY - UNI ===")
            print(f"Institución: {UNI_NAME}")
            print(f"Programas encontrados: {len(potential_links)}")
            print(f"Programas válidos (@tdd-lead): {len(valid_courses)}")
            print(f"Nuevos ingresos: {new_c}")
            print(f"Actualizaciones: {upd_c}")
            print(f"Estado: Proceso completado exitosamente.")
            
        except Exception as e:
            print(f"Error crítico en el proceso: {e}")
        finally:
            await browser.close()

def upsert_to_db(courses_data):
    db = SessionLocal()
    new_count = 0
    update_count = 0
    try:
        for data in courses_data:
            # Buscar por institution_id y name para evitar duplicados
            existing = db.query(Course).filter(
                Course.institution_id == data['institution_id'],
                Course.name == data['name']
            ).first()
            
            price_val = Decimal(str(data['price_pen'])) if data['price_pen'] is not None else None
            
            if existing:
                existing.category = data['category']
                existing.price_pen = price_val
                existing.mode = data['mode']
                existing.address = data['address']
                existing.url = data['url']
                existing.description = data['description']
                existing.duration = data['duration']
                existing.target_audience = data['target_audience']
                existing.syllabus = data['syllabus']
                existing.last_scraped_at = data['last_scraped_at']
                update_count += 1
            else:
                new_course = Course(
                    id=uuid.uuid4(),
                    institution_id=data['institution_id'],
                    name=data['name'],
                    slug=data['slug'],
                    category=data['category'],
                    price_pen=price_val,
                    mode=data['mode'],
                    address=data['address'],
                    url=data['url'],
                    description=data['description'],
                    duration=data['duration'],
                    target_audience=data['target_audience'],
                    syllabus=data['syllabus'],
                    last_scraped_at=data['last_scraped_at']
                )
                db.add(new_course)
                new_count += 1
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[backend-core] ERROR en DB: {e}")
    finally:
        db.close()
    return new_count, update_count

if __name__ == "__main__":
    asyncio.run(scrape_uni())
