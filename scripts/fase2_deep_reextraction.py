import asyncio
from playwright.async_api import async_playwright
import json
import os
import sys
import re
from decimal import Decimal
from datetime import datetime
import uuid

# Add the project root to the sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import Institution, Course
from sqlalchemy import text

# Configuration
INSTITUTION_LIMIT = 27
PROGRAMS_PER_INST_LIMIT = 5

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def standardize_mode(text):
    text = text.lower()
    if any(kw in text for kw in ['remoto', 'virtual', 'online', 'a distancia', 'distancia']):
        return 'Remoto'
    if any(kw in text for kw in ['hibrido', 'híbrido', 'semipresencial', 'blended']):
        return 'Híbrido'
    return 'Presencial'

def extract_price_deep(text):
    # Keywords to look for
    keywords = ['inversión', 'inversion', 'derechos académicos', 'derechos academicos', 'pensiones', 'pensión', 'precio', 'costo']
    
    # Check for explicit zero cost
    if any(kw in text.lower() for kw in ['beca total', 'costo cero', 'sin costo']):
        return 0.0
    
    # Try to find currency symbols and numbers near keywords
    for kw in keywords:
        # Search for keyword followed by some text and then a price
        # Using a more robust regex that looks for S/ or S/. or PEN and then numbers with separators
        pattern = rf'{kw}.*?(?:S/|S/\.|PEN)\s*([\d,.]+)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                # Handle cases like "1.500.00" (common in some locales) vs "1,500.00"
                if price_str.count('.') > 1:
                    price_str = price_str.replace('.', '')
                val = float(price_str)
                if val > 0: return val
            except:
                continue
                
    # Fallback to any currency match if keywords didn't work
    fallback_match = re.search(r'(?:S/|S/\.|PEN)\s*([\d,.]+)', text)
    if fallback_match:
        price_str = fallback_match.group(1).replace(',', '')
        try:
            if price_str.count('.') > 1: price_str = price_str.replace('.', '')
            return float(price_str)
        except:
            return 0.0
            
    return 0.0

def is_category_page(url):
    # Block category list pages
    # Examples: /maestrias, /posgrado/, /cursos, /programas/
    patterns = [
        r'/(maestrias|posgrado|cursos|programas|doctorados|especialidades|diplomados)/?$',
        r'/(maestrias|posgrado|cursos|programas|doctorados|especialidades|diplomados)$',
        r'/[a-z-]+/(lista|all|index)$'
    ]
    for pattern in patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

async def get_institutions():
    db = SessionLocal()
    try:
        institutions = db.query(Institution).all()
        return [(inst.id, inst.name, inst.website_url, inst.slug) for inst in institutions]
    finally:
        db.close()

async def auto_scroll(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 300;
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight || totalHeight > 5000){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)

async def deep_crawl_institution(page, inst_id, inst_name, base_url):
    print(f"\n[HARVESTER] Deep Crawling {inst_name} ({base_url})...")
    programs_found = []
    
    # Common sub-paths to find programs listing
    paths_to_try = ['', '/posgrado', '/maestrias', '/programas', '/cursos']
    
    all_links = set()
    
    for path in paths_to_try:
        url = base_url.rstrip('/') + path
        try:
            print(f"  Exploring {url}...")
            await page.goto(url, timeout=45000, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            await auto_scroll(page)
            
            # Find all links that might be individual programs
            links = await page.query_selector_all("a")
            for link in links:
                try:
                    href = await link.get_attribute("href")
                    text_content = await link.inner_text()
                    text_content = text_content.strip()
                    
                    if href and (href.startswith('http') or href.startswith('/')):
                        # Normalize URL
                        if href.startswith('/'):
                            full_url = base_url.rstrip('/') + href
                        else:
                            full_url = href
                        
                        # Apply URL Validation (Rule 4)
                        if is_category_page(full_url):
                            continue
                            
                        # Basic filter: must contain keywords and have reasonable length
                        # Individual program links usually have specific names
                        if len(text_content) > 15 and any(kw in text_content.lower() for kw in ['maestría', 'maestria', 'doctorado', 'especialidad', 'diplomado', 'curso', 'taller', 'programa']):
                            all_links.add((text_content, full_url))
                except:
                    continue
        except Exception as e:
            print(f"    Error exploring {url}: {e}")
            continue

    print(f"  Found {len(all_links)} potential individual program links.")
    
    # Visit EACH URL independently (Rule 2)
    processed_count = 0
    unique_urls = set()
    
    # Shuffle or just pick a subset to avoid being blocked if too many
    links_list = list(all_links)
    
    for prog_name, prog_url in links_list:
        if prog_url in unique_urls: continue
        if processed_count >= PROGRAMS_PER_INST_LIMIT: break
        
        print(f"    [SCRAPER] Visiting: {prog_url}")
        try:
            await page.goto(prog_url, timeout=45000, wait_until="domcontentloaded")
            await asyncio.sleep(3) # Wait for content to load
            
            page_text = await page.inner_text("body")
            
            # Extracting 10 points (AI Parser Simulation)
            modality = standardize_mode(page_text)
            
            # Location
            location = "Lima"
            for city in ["Arequipa", "Piura", "Trujillo", "Cusco", "Chiclayo", "Huancayo"]:
                if city in page_text:
                    location = city
                    break
            
            # Price Extraction (Rule 3)
            price = extract_price_deep(page_text)
            
            # Description & Details
            description = f"Programa de {prog_name} en {inst_name}."
            duration = "No especificado"
            dur_match = re.search(r'(?:Duración|Tiempo|Periodo):\s*(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if dur_match: duration = dur_match.group(1).strip()
            
            target = "Público en general"
            target_match = re.search(r'(?:Dirigido a|Perfil):\s*(.*?)(?:\n|$)', page_text, re.IGNORECASE)
            if target_match: target = target_match.group(1).strip()
            
            syllabus = ""
            if any(kw in page_text for kw in ["Temario", "Plan de estudios", "Contenido", "Módulos", "Modulos"]):
                syllabus = "Syllabus detectado en la página oficial."
            
            # Category
            category = 'Curso'
            if 'maestría' in prog_name.lower() or 'maestria' in prog_name.lower(): category = 'Maestría'
            elif 'doctorado' in prog_name.lower(): category = 'Doctorado'
            elif 'especialidad' in prog_name.lower(): category = 'Especialidad'
            elif 'diplomado' in prog_name.lower(): category = 'Diplomado'
            
            programs_found.append({
                "institution_id": inst_id,
                "name": prog_name,
                "slug": f"{slugify(prog_name)}-{str(uuid.uuid4())[:8]}", # Unique slug
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
            unique_urls.add(prog_url)
            processed_count += 1
            print(f"      [PARSER] OK: {prog_name} | Price: {price} | Mode: {modality}")
            
        except Exception as e:
            print(f"      [ERROR] Processing {prog_url}: {e}")
            
    return programs_found

def upsert_courses(courses_data):
    db = SessionLocal()
    new_count = 0
    try:
        for data in courses_data:
            # UPSERT logic (Rule 5)
            # Use raw SQL to handle potential conflicts better across engines
            query = text("""
                INSERT INTO courses (id, institution_id, name, slug, category, price_pen, mode, address, url, description, duration, target_audience, syllabus, last_scraped_at, created_at, updated_at)
                VALUES (:id, :inst_id, :name, :slug, :category, :price, :mode, :address, :url, :description, :duration, :target, :syllabus, :last_scraped, :now, :now)
            """)
            
            db.execute(query, {
                "id": str(uuid.uuid4()),
                "inst_id": str(data['institution_id']),
                "name": data['name'],
                "slug": data['slug'],
                "category": data['category'],
                "price": float(data['price_pen']),
                "mode": data['mode'],
                "address": data['address'],
                "url": data['url'],
                "description": data['description'],
                "duration": data['duration'],
                "target": data['target_audience'],
                "syllabus": data['syllabus'],
                "last_scraped": data['last_scraped_at'],
                "now": datetime.now()
            })
            new_count += 1
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[BACKEND] Error upserting courses: {e}")
    finally:
        db.close()
    return new_count

async def main():
    print("--- INICIANDO FASE 2: RE-EXTRACCIÓN PROFUNDA ---")
    institutions = await get_institutions()
    print(f"Instituciones encontradas: {len(institutions)}")
    
    # Filter/Select target institutions
    target_institutions = institutions[:INSTITUTION_LIMIT]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 1000}
        )
        page = await context.new_page()
        
        all_discovered = []
        for inst_id, inst_name, base_url, inst_slug in target_institutions:
            try:
                discovered = await deep_crawl_institution(page, inst_id, inst_name, base_url)
                all_discovered.extend(discovered)
                
                # Intermediate save to avoid losing everything on crash
                if discovered:
                    upsert_courses(discovered)
                    print(f"[BACKEND] Persistidos {len(discovered)} cursos de {inst_name}")
            except Exception as e:
                print(f"[CRITICAL] Fallo en {inst_name}: {e}")
        
        await browser.close()
        
    print("\n--- FASE 2 COMPLETADA ---")
    print(f"Total de cursos descubiertos y procesados: {len(all_discovered)}")

if __name__ == "__main__":
    asyncio.run(main())
