import asyncio
import os
import sys
import re
import json
from datetime import datetime
from decimal import Decimal
from playwright.async_api import async_playwright
from sqlalchemy import func

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api.models import Institution, Course

# Configuration
BATCH_SIZE = 5
MAX_PROGRAMS_PER_INST = 5
TIMEOUT = 45000

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
    """
    Standardize cost extraction.
    If explicitly free, return 0.0.
    If price found, return float.
    Else return None.
    """
    text_lower = text.lower()
    # Explicitly free
    if any(kw in text_lower for kw in ['gratis', 'sin costo', 'free', 'beca 100%']):
        return 0.0
    
    # Try to find currency symbols and numbers
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
    
    return None # Will be stored as null in DB for 'Consultar precio'

async def get_pending_institutions():
    db = SessionLocal()
    try:
        # Institutions that have 0 courses
        pending = db.query(Institution).outerjoin(Course).group_by(Institution.id).having(func.count(Course.id) == 0).all()
        return [(inst.id, inst.name, inst.website_url, inst.slug) for inst in pending]
    finally:
        db.close()

async def deep_crawl_institution(page, inst_id, inst_name, base_url, inst_slug):
    print(f"\n[CRAWLER] Iniciando Deep Crawl para: {inst_name} ({base_url})")
    programs_discovered = []
    
    # Common sub-paths to find programs
    paths_to_try = ['', '/posgrado', '/maestrias', '/programas', '/cursos', '/educacion-continua']
    
    all_potential_links = set()
    
    for path in paths_to_try:
        url = base_url.rstrip('/') + path
        try:
            print(f"  [EXPLORAR] {url}")
            await page.goto(url, timeout=TIMEOUT, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # Find all links
            links = await page.query_selector_all("a")
            for link in links:
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
                    if len(text) > 15 and any(kw in text.lower() for kw in ['maestría', 'maestria', 'doctorado', 'especialidad', 'diplomado', 'curso', 'taller', 'programa']):
                        # Avoid external links like social media
                        if inst_slug in full_url.lower() or base_url.split('//')[-1].split('/')[0] in full_url:
                            all_potential_links.add((text, full_url))
        except Exception as e:
            print(f"    Error explorando {url}: {e}")
            continue

    print(f"  [RESULTADO] Se encontraron {len(all_potential_links)} enlaces potenciales de programas.")
    
    # Process up to MAX_PROGRAMS_PER_INST
    processed_count = 0
    for prog_name, prog_url in list(all_potential_links):
        if processed_count >= MAX_PROGRAMS_PER_INST:
            break
            
        print(f"  [DETALLE] Procesando programa ({processed_count+1}/{MAX_PROGRAMS_PER_INST}): {prog_name}")
        try:
            await page.goto(prog_url, timeout=TIMEOUT, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            page_text = await page.inner_text("body")
            
            # Extraction logic
            price = extract_price(page_text)
            mode = standardize_mode(page_text)
            
            # Location
            location = "Lima" # Default
            for city in ["Arequipa", "Piura", "Trujillo", "Cusco", "Chiclayo", "Iquitos"]:
                if city in page_text:
                    location = city
                    break
            
            # Description
            description = ""
            desc_match = re.search(r'(?:Descripción|Resumen|Sobre el programa|Presentación):(.*?)(?:\n\n|\n[A-Z])', page_text, re.DOTALL | re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()[:500]
            else:
                # Fallback: first 200 chars of body
                description = page_text[:200].replace('\n', ' ').strip() + "..."
            
            # Duration
            duration = "No especificado"
            dur_match = re.search(r'(?:Duración|Tiempo|Periodo):(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if dur_match:
                duration = dur_match.group(1).strip()
            
            # Target Audience
            target = "Público en general"
            target_match = re.search(r'(?:Dirigido a|Perfil del postulante):(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if target_match:
                target = target_match.group(1).strip()
            
            # Syllabus (Temario)
            syllabus = ""
            if any(kw in page_text.lower() for kw in ["temario", "plan de estudios", "malla curricular", "contenido", "módulos"]):
                syllabus = "Temario disponible en el sitio oficial."
            
            # Category
            category = 'Curso'
            p_name_lower = prog_name.lower()
            if 'maestría' in p_name_lower or 'maestria' in p_name_lower: category = 'Maestría'
            elif 'doctorado' in p_name_lower: category = 'Doctorado'
            elif 'especialidad' in p_name_lower: category = 'Especialidad'
            elif 'diplomado' in p_name_lower: category = 'Diplomado'
            
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
            # Check if exists by name and institution
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
    pending_insts = await get_pending_institutions()
    print(f"=== OPERACIÓN YACHACHIY TOTAL: DEEP CRAWL MASIVO ===")
    print(f"Instituciones pendientes encontradas: {len(pending_insts)}")
    
    if not pending_insts:
        print("No hay instituciones pendientes de procesamiento. Tarea completada.")
        return

    # Process in batches of 5
    for i in range(0, len(pending_insts), BATCH_SIZE):
        batch = pending_insts[i:i + BATCH_SIZE]
        print(f"\n--- PROCESANDO LOTE {i//BATCH_SIZE + 1} ({len(batch)} instituciones) ---")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            all_batch_courses = []
            for inst_id, inst_name, base_url, inst_slug in batch:
                page = await context.new_page()
                try:
                    discovered = await deep_crawl_institution(page, inst_id, inst_name, base_url, inst_slug)
                    all_batch_courses.extend(discovered)
                except Exception as e:
                    print(f"Error crítico para {inst_name}: {e}")
                finally:
                    await page.close()
            
            await browser.close()
            
            if all_batch_courses:
                new_c, upd_c = upsert_courses(all_batch_courses)
                print(f"\n[LOTE COMPLETADO] {new_c} cursos nuevos creados, {upd_c} actualizados.")
                
                # Validation (TDD Lead simulation)
                syllabus_ok = [c for c in all_batch_courses if c['syllabus']]
                links_ok = [c for c in all_batch_courses if c['url'].startswith('http')]
                
                print(f"  Validación de Integridad:")
                print(f"  - Cursos con Temario: {len(syllabus_ok)}/{len(all_batch_courses)}")
                print(f"  - Enlaces Funcionales (formato): {len(links_ok)}/{len(all_batch_courses)}")
                
                if len(all_batch_courses) > 0 and (len(syllabus_ok)/len(all_batch_courses)) > 0.5:
                    print("  - Resultado: INTEGRIDAD ACEPTABLE.")
                else:
                    print("  - Resultado: REVISIÓN REQUERIDA (Baja detección de temarios).")
            else:
                print("\n[LOTE COMPLETADO] No se descubrieron cursos en este lote.")

if __name__ == "__main__":
    asyncio.run(main())
