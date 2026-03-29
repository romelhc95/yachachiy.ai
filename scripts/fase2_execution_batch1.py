
import asyncio
import os
import sys
import re
import json
from datetime import datetime
from decimal import Decimal
from playwright.async_api import async_playwright
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker

# Configurar DATABASE_URL para MySQL local 3307 explícitamente para LOCAL-FIRST
os.environ["DATABASE_URL"] = "mysql+pymysql://root:@localhost:3307/yachachiy"

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import Institution, Course

# Configuration
MAX_PROGRAMS_PER_INST = 10
TIMEOUT = 60000

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
            if val > 0:
                return val
        except:
            pass
    return None

async def get_next_pending_institution():
    db = SessionLocal()
    try:
        # Encuentra la primera institución que no tenga cursos registrados
        pending = db.query(Institution).outerjoin(Course).group_by(Institution.id).having(func.count(Course.id) == 0).first()
        if pending:
            return (pending.id, pending.name, pending.website_url, pending.slug)
        return None
    finally:
        db.close()

async def deep_crawl_institution(page, inst_id, inst_name, base_url, inst_slug):
    print(f"\n[CRAWLER] Iniciando Deep Crawl para: {inst_name} ({base_url})")
    programs_discovered = []
    
    # Common sub-paths to find programs
    paths_to_try = ['', '/posgrado', '/maestrias', '/programas', '/cursos', '/educacion-continua', '/admision']
    
    all_potential_links = set()
    
    for path in paths_to_try:
        url = base_url.rstrip('/') + path
        try:
            print(f"  [EXPLORAR] Intentando: {url}")
            await page.goto(url, timeout=TIMEOUT, wait_until="networkidle")
            await asyncio.sleep(3)
            
            # Find all links
            links = await page.query_selector_all("a")
            for link in links:
                try:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    text = text.strip()
                    
                    if href and (href.startswith('http') or href.startswith('/')):
                        # Normalize URL
                        if href.startswith('/'):
                            full_url = base_url.rstrip('/') + href
                        else:
                            full_url = href
                        
                        # Filter: must contain keywords and have reasonable text length
                        if len(text) > 10 and any(kw in text.lower() for kw in ['maestría', 'maestria', 'doctorado', 'especialidad', 'diplomado', 'curso', 'taller', 'programa']):
                            # Avoid external links
                            if inst_slug in full_url.lower() or base_url.split('//')[-1].split('/')[0] in full_url:
                                all_potential_links.add((text, full_url))
                except:
                    continue
        except Exception as e:
            print(f"    Error explorando {url}: {e}")
            continue

    print(f"  [RESULTADO] Se encontraron {len(all_potential_links)} enlaces potenciales de programas.")
    
    # Process up to MAX_PROGRAMS_PER_INST
    processed_count = 0
    for prog_name, prog_url in list(all_potential_links):
        if processed_count >= MAX_PROGRAMS_PER_INST:
            break
            
        print(f"  [DETALLE] ({processed_count+1}/{MAX_PROGRAMS_PER_INST}) {prog_name} -> {prog_url}")
        try:
            await page.goto(prog_url, timeout=TIMEOUT, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            page_text = await page.inner_text("body")
            
            # 10 Puntos Críticos Extraction
            price = extract_price(page_text)
            mode = standardize_mode(page_text)
            
            # Location (Sede)
            location = "Lima" 
            for city in ["Arequipa", "Piura", "Trujillo", "Cusco", "Chiclayo", "Iquitos", "Tarapoto", "Juliaca", "Pucallpa"]:
                if city in page_text:
                    location = city
                    break
            
            # Description
            description = ""
            desc_match = re.search(r'(?:Descripción|Resumen|Sobre el programa|Presentación|Objetivo):(.*?)(?:\n\n|\n[A-Z])', page_text, re.DOTALL | re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()[:1000]
            else:
                description = page_text[:500].replace('\n', ' ').strip() + "..."
            
            # Duration (Tiempo)
            duration = "No especificado"
            dur_match = re.search(r'(?:Duración|Tiempo|Periodo|Meses|Semanas):(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if dur_match:
                duration = dur_match.group(1).strip()
            
            # Target Audience (Público)
            target = "Público en general"
            target_match = re.search(r'(?:Dirigido a|Perfil del postulante|Público objetivo):(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if target_match:
                target = target_match.group(1).strip()
            
            # Syllabus (Temario)
            syllabus = ""
            syllabus_keywords = ["temario", "plan de estudios", "malla curricular", "contenido", "módulos", "asignaturas"]
            if any(kw in page_text.lower() for kw in syllabus_keywords):
                syllabus = "Estructura curricular detectada en el sitio oficial."
                # Intentar extraer algo más específico si es posible
                syllabus_match = re.search(r'(?:Plan de estudios|Malla curricular|Contenido del programa)(.*?)(?:\n\n|\n[A-Z])', page_text, re.DOTALL | re.IGNORECASE)
                if syllabus_match:
                    syllabus = syllabus_match.group(1).strip()[:500]
            
            # Category
            category = 'Curso'
            p_name_lower = prog_name.lower()
            if 'maestría' in p_name_lower or 'maestria' in p_name_lower: category = 'Maestría'
            elif 'doctorado' in p_name_lower: category = 'Doctorado'
            elif 'especialidad' in p_name_lower: category = 'Especialidad'
            elif 'diplomado' in p_name_lower: category = 'Diplomado'
            elif 'taller' in p_name_lower: category = 'Taller'
            
            programs_discovered.append({
                "institution_id": inst_id,
                "name": prog_name,
                "slug": slugify(prog_name + "-" + inst_slug),
                "category": category,
                "price_pen": price,
                "mode": mode,
                "address": location,
                "url": prog_url,
                "description": description,
                "duration": duration,
                "target_audience": target,
                "syllabus": syllabus,
                "last_scraped_at": datetime.now()
            })
            processed_count += 1
            
        except Exception as e:
            print(f"    Error procesando detalle {prog_url}: {e}")
            
    return programs_discovered

def upsert_courses(courses_data):
    db = SessionLocal()
    new_count = 0
    update_count = 0
    try:
        for data in courses_data:
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
        print(f"[ERROR] Error al guardar en DB: {e}")
    finally:
        db.close()
    return new_count, update_count

async def main():
    print(f"=== OPERACIÓN YACHACHIY: LOTE ATÓMICO (BATCH SIZE = 1) ===")
    
    inst_info = await get_next_pending_institution()
    
    if not inst_info:
        print("No hay instituciones pendientes. Operación terminada.")
        return

    inst_id, inst_name, base_url, inst_slug = inst_info
    print(f"INSTITUCIÓN SELECCIONADA: {inst_name} ({base_url})")

    async with async_playwright() as p:
        # Usar un navegador real para evitar bloqueos básicos
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        try:
            discovered = await deep_crawl_institution(page, inst_id, inst_name, base_url, inst_slug)
            
            if discovered:
                new_c, upd_c = upsert_courses(discovered)
                print(f"\n[ÉXITO] {new_c} cursos nuevos creados, {upd_c} actualizados para {inst_name}.")
            else:
                print(f"\n[AVISO] No se descubrieron cursos para {inst_name}. Verifique selectores o estructura web.")
                # Opcional: Marcar como procesada con una entrada dummy si se quiere saltar
        except Exception as e:
            print(f"Error crítico procesando {inst_name}: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
