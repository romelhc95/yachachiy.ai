import asyncio
from playwright.async_api import async_playwright
from api.database import SessionLocal
from api.models import Institution, Course
from decimal import Decimal
from datetime import datetime
import re

async def classify_category(name):
    name_lower = name.lower()
    if any(kw in name_lower for kw in ['maestria', 'maestría', 'master', 'magister']):
        return 'Maestría'
    if any(kw in name_lower for kw in ['doctorado', 'phd']):
        return 'Doctorado'
    if any(kw in name_lower for kw in ['especialidad', 'especialización', 'especializacion']):
        return 'Especialidad'
    if any(kw in name_lower for kw in ['diplomado']):
        return 'Diplomado'
    return 'Curso'

async def discover_programs(page, url, institution_slug):
    print(f"Discovering programs at {url} for {institution_slug}...")
    try:
        await page.goto(url, timeout=60000)
        await asyncio.sleep(5) # Wait for JS
        
        # Generic discovery logic: find all links that look like programs
        # and titles that might be course names
        items = []
        
        # Strategy 1: Look for links that contain headers or titles
        links = await page.query_selector_all("a")
        for link in links:
            text = await link.inner_text()
            text = text.strip().replace('\n', ' ')
            href = await link.get_attribute("href")
            
            if len(text) > 10 and len(text) < 150 and href and href.startswith('http'):
                category = await classify_category(text)
                # Only add if it's a likely program name (not 'contactanos', etc)
                if any(kw in text.lower() for kw in ['maestria', 'maestría', 'doctorado', 'especialidad', 'curso', 'diplomado']):
                    items.append({
                        "name": text,
                        "category": category,
                        "institution_slug": institution_slug,
                        "url": href, # Specific URL captured here
                        "price": 0,
                        "mode": "Remoto"
                    })
        
        # Fallback: Strategy 2 (If no links found with keywords, try headers but this is less precise for URLs)
        if not items:
            headers = await page.query_selector_all("h2, h3")
            for h in headers:
                text = await h.inner_text()
                text = text.strip().replace('\n', ' ')
                if len(text) > 10 and len(text) < 100:
                    category = await classify_category(text)
                    items.append({
                        "name": text,
                        "category": category,
                        "institution_slug": institution_slug,
                        "url": url,
                        "price": 0,
                        "mode": "Remoto"
                    })
        
        return items
    except Exception as e:
        print(f"Error at {url}: {e}")
        return []

def save_programs(programs):
    count_new = 0
    count_updated = 0
    for p in programs:
        db = SessionLocal()
        try:
            inst = db.query(Institution).filter(Institution.slug == p['institution_slug']).first()
            if not inst: continue
            
            slug = re.sub(r'[^a-z0-9]+', '-', p['name'].lower()).strip('-')
            
            existing = db.query(Course).filter(Course.institution_id == inst.id, Course.name == p['name']).first()
            if existing:
                existing.category = p['category']
                existing.url = p['url']
                existing.last_scraped_at = datetime.now()
                count_updated += 1
            else:
                course = Course(
                    institution_id=inst.id,
                    name=p['name'],
                    slug=slug,
                    category=p['category'],
                    price_pen=Decimal("0"),
                    mode=p['mode'],
                    address=inst.address,
                    url=p['url'],
                    last_scraped_at=datetime.now()
                )
                db.add(course)
                count_new += 1
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving {p['name']}: {e}")
        finally:
            db.close()
    print(f"Finished: {count_new} new, {count_updated} updated.")

async def main():
    institutions_to_scan = [
        ("pucp", "https://posgrado.pucp.edu.pe/programas/maestrias/"),
        ("upn", "https://www.upn.edu.pe/posgrado/maestrias"),
        ("usmp", "https://usmp.edu.pe/posgrado/"),
        ("esan", "https://www.esan.edu.pe/maestrias/"),
        ("uni", "http://www.posgrado.uni.edu.pe/")
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        all_programs = []
        for slug, url in institutions_to_scan:
            progs = await discover_programs(page, url, slug)
            all_programs.extend(progs)
        
        save_programs(all_programs)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
