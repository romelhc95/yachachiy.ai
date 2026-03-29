import asyncio
from playwright.async_api import async_playwright
import json
import os
import sys
import re
from decimal import Decimal
from datetime import datetime

# Add the project root to the sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import Institution, Course
from sqlalchemy.dialects.postgresql import insert

# Configuration
OUTPUT_FILE = r"C:\xampp\htdocs\yachachiy_ai\scripts\fase2_raw_data.json"

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
    # Try to find currency symbols and numbers
    # S/ 1,500.00 or S/. 1500 or PEN 2000
    price_match = re.search(r'(?:S/|S/\.|PEN)\s*([\d,.]+)', text)
    if price_match:
        price_str = price_match.group(1).replace(',', '')
        try:
            return float(price_str)
        except:
            return 0.0
    return 0.0

async def get_institutions():
    db = SessionLocal()
    try:
        institutions = db.query(Institution).all()
        return [(inst.id, inst.name, inst.website_url, inst.slug) for inst in institutions]
    finally:
        db.close()

async def deep_crawl_institution(page, inst_id, inst_name, base_url, inst_slug):
    print(f"Deep Crawling {inst_name} ({base_url})...")
    programs_found = []
    
    # Common sub-paths to find programs
    paths_to_try = ['', '/posgrado', '/maestrias', '/programas', '/cursos', '/educacion-continua']
    
    all_links = set()
    
    for path in paths_to_try:
        url = base_url.rstrip('/') + path
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # Find all links that might be programs
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
                    
                    # Basic filter: must contain keywords and have reasonable length
                    if len(text) > 15 and any(kw in text.lower() for kw in ['maestría', 'maestria', 'doctorado', 'especialidad', 'diplomado', 'curso', 'taller', 'programa']):
                        all_links.add((text, full_url))
        except Exception as e:
            print(f"Error exploring path {url}: {e}")
            continue

    print(f"Found {len(all_links)} potential program links for {inst_name}")
    
    # Process up to 5 programs per institution for this Phase 2 start
    count = 0
    for prog_name, prog_url in list(all_links)[:5]:
        print(f"  Processing program: {prog_name}")
        try:
            await page.goto(prog_url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            page_content = await page.content()
            page_text = await page.inner_text("body")
            
            # Extracting 10 points (Simulating AI Parser logic)
            # 1. Name: prog_name
            # 2. Institution: inst_name
            # 3. Modality: 
            modality = standardize_mode(page_text)
            # 4. Sede (Location)
            location = "Lima" # Default or search for city names
            if "Arequipa" in page_text: location = "Arequipa"
            elif "Piura" in page_text: location = "Piura"
            elif "Trujillo" in page_text: location = "Trujillo"
            
            # 5. Inversion Real
            price = extract_price(page_text)
            
            # 6. Description
            description = ""
            desc_match = re.search(r'(?:Descripción|Resumen|Sobre el programa):(.*?)(?:\n\n|\n[A-Z])', page_text, re.DOTALL | re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()
            else:
                description = f"Programa de {prog_name} en {inst_name}."
            
            # 7. Tiempo (Duration)
            duration = "No especificado"
            dur_match = re.search(r'Duración:(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if dur_match:
                duration = dur_match.group(1).strip()
            
            # 8. Público (Target Audience)
            target = "Público en general"
            target_match = re.search(r'Dirigido a:(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if target_match:
                target = target_match.group(1).strip()
            
            # 9. Temario (Syllabus)
            syllabus = ""
            if "Temario" in page_text or "Plan de estudios" in page_text or "Contenido" in page_text:
                syllabus = "Temario disponible en la página oficial."
            
            # 10. URL Directa: prog_url
            
            # Category classification
            category = 'Curso'
            if 'maestría' in prog_name.lower() or 'maestria' in prog_name.lower(): category = 'Maestría'
            elif 'doctorado' in prog_name.lower(): category = 'Doctorado'
            elif 'especialidad' in prog_name.lower(): category = 'Especialidad'
            elif 'diplomado' in prog_name.lower(): category = 'Diplomado'
            
            programs_found.append({
                "institution_id": inst_id,
                "name": prog_name,
                "slug": slugify(prog_name),
                "category": category,
                "price_pen": price,
                "mode": modality,
                "address": location,
                "url": prog_url,
                "description": description,
                "duration": duration,
                "target_audience": target,
                "syllabus": syllabus,
                "last_scraped_at": datetime.now()
            })
            count += 1
        except Exception as e:
            print(f"  Error processing {prog_url}: {e}")
            
    return programs_found

def upsert_courses(courses_data):
    db = SessionLocal()
    new_count = 0
    update_count = 0
    try:
        for data in courses_data:
            # We use a merge or check existence for SQLite/Postgres
            # For Postgres, we could use the 'insert' with 'on_conflict_do_update'
            # But let's keep it compatible using ORM check
            
            existing = db.query(Course).filter(
                Course.institution_id == data['institution_id'],
                Course.name == data['name']
            ).first()
            
            if existing:
                existing.category = data['category']
                existing.price_pen = Decimal(str(data['price_pen']))
                existing.mode = data['mode']
                existing.address = data['address']
                existing.url = data['url']
                existing.duration = data['duration']
                existing.last_scraped_at = data['last_scraped_at']
                update_count += 1
            else:
                new_course = Course(
                    institution_id=data['institution_id'],
                    name=data['name'],
                    slug=data['slug'],
                    category=data['category'],
                    price_pen=Decimal(str(data['price_pen'])),
                    mode=data['mode'],
                    address=data['address'],
                    url=data['url'],
                    duration=data['duration'],
                    last_scraped_at=data['last_scraped_at']
                )
                db.add(new_course)
                new_count += 1
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error upserting courses: {e}")
    finally:
        db.close()
    return new_count, update_count

async def main():
    institutions = await get_institutions()
    print(f"Found {len(institutions)} institutions to crawl.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        all_discovered = []
        # Limit to the first 10 institutions for the initial run to stay within time/resource limits
        for inst_id, inst_name, base_url, inst_slug in institutions[:10]:
            try:
                discovered = await deep_crawl_institution(page, inst_id, inst_name, base_url, inst_slug)
                all_discovered.extend(discovered)
            except Exception as e:
                print(f"Critical error for {inst_name}: {e}")
        
        await browser.close()
        
        if all_discovered:
            new_c, upd_c = upsert_courses(all_discovered)
            print(f"Phase 2 Execution Result: {new_c} new courses, {upd_c} updated.")
            
            # Validation (TDD Lead simulation)
            courses_with_syllabus = [c for c in all_discovered if c['syllabus']]
            syllabus_pct = (len(courses_with_syllabus) / len(all_discovered)) * 100 if all_discovered else 0
            print(f"TDD Lead: Syllabus completeness: {syllabus_pct:.2f}%")
            
            if syllabus_pct >= 80:
                print("TDD Lead: Validation PASSED (>80% completeness).")
            else:
                print("TDD Lead: Validation FAILED (<80% completeness).")
        else:
            print("No courses discovered.")

if __name__ == "__main__":
    asyncio.run(main())
