import asyncio
from playwright.async_api import async_playwright
import re
import os
import sys
from decimal import Decimal
from datetime import datetime
import uuid

# Add the project root to the sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import Institution, Course
from sqlalchemy.dialects.mysql import insert as mysql_insert

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
    # Expanded regex for Peruvian currency
    price_patterns = [
        r'(?:S/|S/\.|PEN|Soles)\s*([\d,.]+)',
        r'Inversión:\s*(?:S/|S/\.|PEN)\s*([\d,.]+)',
        r'Precio:\s*(?:S/|S/\.|PEN)\s*([\d,.]+)',
        r'Costo:\s*(?:S/|S/\.|PEN)\s*([\d,.]+)'
    ]
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                # Basic validation: price should be reasonable
                val = float(price_str)
                if 100 < val < 200000:
                    return val
            except:
                continue
    return 0.0

def extract_field(text, keywords):
    for kw in keywords:
        pattern = rf'{kw}:?\s*(.*?)(?:\n|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            val = match.group(1).strip()
            if len(val) > 2:
                return val[:500] # Limit length
    return "No especificado"

async def deep_crawl_institution(page, inst_id, inst_name, base_url):
    print(f"\n--- [Discovery] {inst_name} ({base_url}) ---")
    
    # Common paths to find programs
    paths = ['', '/posgrado', '/educacion-continua', '/maestrias', '/cursos', '/programas-academicos', '/diplomados']
    links_to_process = []
    
    # Discovery Phase
    for path in paths:
        url = base_url.rstrip('/') + path
        try:
            print(f"  Exploring {url}...")
            await page.goto(url, timeout=45000, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # Look for program links
            links = await page.query_selector_all("a")
            for link in links:
                try:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    text = text.strip()
                    
                    if not href or len(text) < 15: continue
                    
                    # Normalize URL
                    if href.startswith('/'):
                        full_url = base_url.rstrip('/') + ('' if href.startswith('/') else '/') + href
                        if '//' in full_url[8:]: full_url = full_url.replace('//', '/') # fix triple slashes
                    elif not href.startswith('http'):
                        continue
                    else:
                        full_url = href
                    
                    # Keywords for academic programs
                    keywords = ['maestría', 'maestria', 'doctorado', 'diplomado', 'especialidad', 'programa', 'curso', 'taller', 'expert']
                    if any(kw in text.lower() for kw in keywords) and (base_url.split('//')[1].split('/')[0] in full_url):
                        if not any(l[1] == full_url for l in links_to_process):
                            links_to_process.append((text, full_url))
                except:
                    continue
        except Exception as e:
            print(f"  Error exploring {url}: {e}")
    
    print(f"  Discovered {len(links_to_process)} candidate links.")
    
    results = []
    # Process up to 10 programs per institution for a solid initial database
    for prog_name, prog_url in links_to_process[:10]:
        print(f"    - [Extraction] {prog_name}")
        try:
            await page.goto(prog_url, timeout=45000, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            page_text = await page.inner_text("body")
            
            # [Verification] Skip news/blogs/non-academic
            if any(kw in page_text.lower()[:500] for kw in ['noticias', 'evento pasado', 'comunicado']):
                print(f"      Skipping non-academic content.")
                continue

            # [Parsing] 10 Critical Points
            price = extract_price(page_text)
            syllabus = extract_field(page_text, ['Temario', 'Plan de estudios', 'Contenido', 'Módulos', 'Estructura'])
            duration = extract_field(page_text, ['Duración', 'Tiempo', 'Periodo', 'Horas'])
            mode = standardize_mode(page_text)
            address = extract_field(page_text, ['Sede', 'Lugar', 'Dirección', 'Campus'])
            target = extract_field(page_text, ['Dirigido a', 'Perfil del postulante', 'Público', 'Requisitos'])
            reqs = extract_field(page_text, ['Requisitos', 'Perfil de ingreso', 'Pre-requisitos'])
            cert = extract_field(page_text, ['Certificación', 'Grado', 'Título', 'Certificado'])
            start = extract_field(page_text, ['Inicio', 'Fecha de inicio', 'Próximo inicio'])
            benefits = extract_field(page_text, ['Beneficios', 'Por qué estudiar', 'Ventajas'])
            
            description = extract_field(page_text, ['Descripción', 'Sobre el programa', 'Resumen', 'Presentación'])
            if description == "No especificado":
                description = f"Programa de {prog_name} en {inst_name}."

            category = 'Curso'
            p_name_low = prog_name.lower()
            if 'maestría' in p_name_low or 'maestria' in p_name_low: category = 'Maestría'
            elif 'doctorado' in p_name_low: category = 'Doctorado'
            elif 'diplomado' in p_name_low: category = 'Diplomado'
            elif 'especialidad' in p_name_low: category = 'Especialidad'

            results.append({
                "institution_id": inst_id,
                "name": prog_name,
                "slug": slugify(f"{inst_name}-{prog_name}"[:100]),
                "category": category,
                "price_pen": price,
                "mode": mode,
                "address": address if address != "No especificado" else "Lima",
                "url": prog_url,
                "description": description,
                "syllabus": syllabus,
                "target_audience": target,
                "requirements": reqs,
                "certification": cert,
                "start_date": start,
                "benefits": benefits,
                "duration": duration,
                "last_scraped_at": datetime.now()
            })
        except Exception as e:
            print(f"      Error processing {prog_url}: {e}")
            
    return results

def upsert_courses(courses):
    db = SessionLocal()
    new_c = 0
    upd_c = 0
    try:
        for c_data in courses:
            # Use MySQL-specific UPSERT if available, or generic ORM
            if "mysql" in str(engine.url):
                stmt = mysql_insert(Course).values(
                    id=str(uuid.uuid4()),
                    **{k: (Decimal(str(v)) if k == 'price_pen' else v) for k, v in c_data.items()}
                ).on_duplicate_key_update(
                    category=c_data['category'],
                    price_pen=Decimal(str(c_data['price_pen'])),
                    mode=c_data['mode'],
                    address=c_data['address'],
                    url=c_data['url'],
                    description=c_data['description'],
                    syllabus=c_data['syllabus'],
                    target_audience=c_data['target_audience'],
                    requirements=c_data['requirements'],
                    certification=c_data['certification'],
                    start_date=c_data['start_date'],
                    benefits=c_data['benefits'],
                    duration=c_data['duration'],
                    last_scraped_at=c_data['last_scraped_at']
                )
                db.execute(stmt)
                new_c += 1 # Approximation for MySQL core execute
            else:
                existing = db.query(Course).filter(
                    Course.institution_id == c_data['institution_id'],
                    Course.name == c_data['name']
                ).first()
                
                if existing:
                    for key, value in c_data.items():
                        if key == 'price_pen':
                            setattr(existing, key, Decimal(str(value)))
                        else:
                            setattr(existing, key, value)
                    upd_c += 1
                else:
                    new_course = Course(
                        id=str(uuid.uuid4()),
                        **{k: (Decimal(str(v)) if k == 'price_pen' else v) for k, v in c_data.items()}
                    )
                    db.add(new_course)
                    new_c += 1
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during upsert: {e}")
    finally:
        db.close()
    return new_c, upd_c

async def main():
    db = SessionLocal()
    institutions = db.query(Institution).all()
    inst_info = [(i.id, i.name, i.website_url) for i in institutions]
    db.close()
    
    if not inst_info:
        print("No institutions found in DB. Run seed script first.")
        return

    print(f"=== Operación Yachachiy: Extracción de Alta Fidelidad ===")
    print(f"Target: {len(inst_info)} institutions")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        institution_results = {}
        
        for inst_id, name, url in inst_info:
            page = await context.new_page()
            try:
                discovered_courses = await deep_crawl_institution(page, inst_id, name, url)
                if discovered_courses:
                    n, u = upsert_courses(discovered_courses)
                    institution_results[name] = f"SUCCESS: {len(discovered_courses)} programs processed ({n} new/updated)"
                else:
                    institution_results[name] = "WARNING: No programs discovered"
            except Exception as e:
                institution_results[name] = f"ERROR: {str(e)}"
            finally:
                await page.close()
            
        await browser.close()
        
        print("\n" + "="*50)
        print("FINAL REPORT: Operación Yachachiy")
        print("="*50)
        for inst, res in institution_results.items():
            print(f"{inst}: {res}")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
