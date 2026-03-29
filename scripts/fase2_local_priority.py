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

from api.database import SessionLocal
from api.models import Institution, Course

# Target Institutions Slugs
TARGET_SLUGS = ['pucp', 'utec', 'esan', 'upn', 'usmp']

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def standardize_mode(text):
    text = text.lower()
    if any(kw in text for kw in ['remoto', 'virtual', 'online', 'a distancia']):
        return 'Remoto'
    if any(kw in text for kw in ['hibrido', 'híbrido', 'semipresencial', 'blended']):
        return 'Híbrido'
    return 'Presencial'

def extract_price(text):
    # Expanded regex for Peruvian currency
    price_patterns = [
        r'(?:S/|S/\.|PEN|Soles)\s*([\d,.]+)',
        r'Inversión:\s*(?:S/|S/\.|PEN)\s*([\d,.]+)',
        r'Precio:\s*(?:S/|S/\.|PEN)\s*([\d,.]+)'
    ]
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                return float(price_str)
            except:
                continue
    return 0.0

def extract_field(text, keywords):
    for kw in keywords:
        pattern = rf'{kw}:(.*?)(?:\n|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    return "No especificado"

async def deep_crawl_institution(page, inst_id, inst_name, base_url):
    print(f"\n--- Deep Crawling: {inst_name} ({base_url}) ---")
    
    # Common paths to find programs
    paths = ['', '/posgrado', '/educacion-continua', '/maestrias', '/cursos']
    links_to_process = []
    
    for path in paths:
        url = base_url.rstrip('/') + path
        try:
            print(f"  Exploring {url}...")
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(1)
            
            # Look for program links
            links = await page.query_selector_all("a")
            for link in links:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                text = text.strip()
                
                if not href or len(text) < 10: continue
                
                # Normalize URL
                if href.startswith('/'):
                    full_url = base_url.rstrip('/') + href
                elif not href.startswith('http'):
                    continue
                else:
                    full_url = href
                
                # Keywords for programs
                keywords = ['maestría', 'maestria', 'doctorado', 'diplomado', 'especialidad', 'programa', 'curso', 'taller']
                if any(kw in text.lower() for kw in keywords) and base_url in full_url:
                    if (text, full_url) not in links_to_process:
                        links_to_process.append((text, full_url))
        except Exception as e:
            print(f"  Error exploring {url}: {e}")
    
    print(f"  Found {len(links_to_process)} candidate links.")
    
    results = []
    # Process up to 3 programs per institution for speed in this batch
    for prog_name, prog_url in links_to_process[:3]:
        print(f"    - Processing: {prog_name}")
        try:
            await page.goto(prog_url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(1)
            
            page_text = await page.inner_text("body")
            
            # 10 Critical Points Extraction
            price = extract_price(page_text) # 1. Inversión Real
            syllabus = extract_field(page_text, ['Temario', 'Plan de estudios', 'Contenido', 'Módulos']) # 2. Temario
            duration = extract_field(page_text, ['Duración', 'Tiempo', 'Periodo']) # 3. Duración
            mode = standardize_mode(page_text) # 4. Modalidad
            address = extract_field(page_text, ['Sede', 'Lugar', 'Dirección']) # 5. Sede
            target = extract_field(page_text, ['Dirigido a', 'Perfil del postulante', 'Público']) # 6. Dirigido a
            reqs = extract_field(page_text, ['Requisitos', 'Perfil de ingreso', 'Pre-requisitos']) # 7. Requisitos
            cert = extract_field(page_text, ['Certificación', 'Grado', 'Título', 'Certificado']) # 8. Certificación
            start = extract_field(page_text, ['Inicio', 'Fecha de inicio', 'Próximo inicio']) # 9. Fecha de inicio
            benefits = extract_field(page_text, ['Beneficios', 'Por qué estudiar', 'Ventajas']) # 10. Beneficios
            
            description = extract_field(page_text, ['Descripción', 'Sobre el programa', 'Resumen'])
            if description == "No especificado":
                description = f"Información sobre {prog_name} en {inst_name}."

            category = 'Curso'
            if 'maestría' in prog_name.lower() or 'maestria' in prog_name.lower(): category = 'Maestría'
            elif 'doctorado' in prog_name.lower(): category = 'Doctorado'
            elif 'diplomado' in prog_name.lower(): category = 'Diplomado'
            elif 'especialidad' in prog_name.lower(): category = 'Especialidad'

            slug = slugify(prog_name)
            
            # Ensure unique slug for this run
            temp_slug = slug
            counter = 1
            while any(c['slug'] == temp_slug and c['institution_id'] == inst_id for c in results):
                temp_slug = f"{slug}-{counter}"
                counter += 1
            slug = temp_slug

            results.append({
                "institution_id": inst_id,
                "name": prog_name,
                "slug": slug,
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
                    id=uuid.uuid4(),
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
    institutions = db.query(Institution).filter(Institution.slug.in_(TARGET_SLUGS)).all()
    inst_info = [(i.id, i.name, i.website_url) for i in institutions]
    db.close()
    
    if not inst_info:
        print("No target institutions found in DB.")
        return

    print(f"Starting crawl for {len(inst_info)} target institutions...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        all_courses = []
        for inst_id, name, url in inst_info:
            discovered = await deep_crawl_institution(page, inst_id, name, url)
            all_courses.extend(discovered)
            
        await browser.close()
        
        if all_courses:
            new_n, upd_n = upsert_courses(all_courses)
            print(f"\nResults: {new_n} new courses, {upd_n} updated.")
            
            # Validation
            print(f"Total courses processed: {len(all_courses)}")
            for c in all_courses:
                print(f"- {c['name']} (Price: {c['price_pen']}, Mode: {c['mode']})")
                # Check for 10 points (syllabus, duration, etc. are part of the dict)
                points = [c['price_pen'], c['syllabus'], c['duration'], c['mode'], c['address'], c['target_audience'], c['requirements'], c['certification'], c['start_date'], c['benefits']]
                filled = [p for p in points if p and p != "No especificado" and p != 0.0]
                print(f"  Data Points Filled: {len(filled)}/10")
        else:
            print("No courses were discovered.")

if __name__ == "__main__":
    asyncio.run(main())
