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
    if any(kw in text for kw in ['hibrido', 'hÃ­brido', 'semipresencial', 'blended']):
        return 'HÃ­brido'
    return 'Presencial'

async def deep_crawl_institution(page, inst_id, inst_name, base_url):
    print(f"DEBUG: Crawling {inst_name} ({base_url})...")
    programs_found = []
    
    # Try just the base URL for this test
    try:
        await page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
        print(f"DEBUG: Page loaded for {inst_name}")
        
        # Find some links
        links = await page.query_selector_all("a")
        print(f"DEBUG: Found {len(links)} links on home page.")
        
        for link in links[:50]: # Check first 50 links
            text = await link.inner_text()
            href = await link.get_attribute("href")
            if text and len(text.strip()) > 10 and any(kw in text.lower() for kw in ['maestria', 'diplomado', 'curso', 'posgrado']):
                print(f"DEBUG: Found potential link: {text.strip()} -> {href}")
                # For this test, let's just create a dummy program data from the home page links
                programs_found.append({
                    "institution_id": inst_id,
                    "name": text.strip(),
                    "slug": slugify(text.strip() + "-" + str(datetime.now().timestamp())),
                    "category": 'MaestrÃ­a' if 'maestria' in text.lower() else 'Curso',
                    "price_pen": 0.0,
                    "mode": 'Presencial',
                    "address": 'Lima',
                    "url": href if href and href.startswith('http') else base_url + (href if href else ''),
                    "description": f"Encontrado en {base_url}",
                    "duration": "No especificado",
                    "last_scraped_at": datetime.now()
                })
                if len(programs_found) >= 2: break
    except Exception as e:
        print(f"DEBUG: Error crawling {inst_name}: {e}")
    
    return programs_found

async def main():
    db = SessionLocal()
    inst = db.query(Institution).first()
    db.close()
    
    if not inst:
        print("DEBUG: No institutions in DB.")
        return

    print(f"DEBUG: Testing with institution: {inst.name}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        discovered = await deep_crawl_institution(page, inst.id, inst.name, inst.website_url)
        print(f"DEBUG: Discovered {len(discovered)} programs.")
        
        if discovered:
            db = SessionLocal()
            try:
                for data in discovered:
                    new_course = Course(**data)
                    db.add(new_course)
                db.commit()
                print(f"DEBUG: Successfully inserted {len(discovered)} courses.")
            except Exception as e:
                db.rollback()
                print(f"DEBUG: Error inserting: {e}")
            finally:
                db.close()
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
