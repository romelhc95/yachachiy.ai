import asyncio
from playwright.async_api import async_playwright
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Warning: DATABASE_URL not set. Database persistence will fail.")

async def scrape_utec(page):
    """Pilot scraper for UTEC"""
    print("Scraping UTEC...")
    await page.goto("https://posgrado.utec.edu.pe/cursos-y-programas", timeout=60000)
    # Wait for dynamic content
    try:
        await page.wait_for_selector(".card1", timeout=20000)
    except Exception:
        print("Timeout waiting for .card1, trying h3...")
        try:
            await page.wait_for_selector("h3", timeout=10000)
        except Exception:
            print("Could not find h3 either.")
    
    courses = await page.query_selector_all(".card1")
    results = []
    
    for course in courses:
        title_elem = await course.query_selector(".card1__title")
        title = await title_elem.inner_text() if title_elem else "N/A"
        
        # Modality
        details_elem = await course.query_selector(".card1__details span")
        details_text = await details_elem.inner_text() if details_elem else ""
        mode = "Presencial"
        if "online" in details_text.lower() or "remoto" in details_text.lower():
            mode = "Remoto"
        elif "híbrido" in details_text.lower():
            mode = "Híbrido"
        
        results.append({
            "name": title.strip(),
            "institution_slug": "utec",
            "price_pen": 0, # To be filled by AI Parser later
            "mode": mode,
            "address": "Barranco, Lima"
        })
    
    return results

async def scrape_upc(page):
    """Pilot scraper for UPC"""
    print("Scraping UPC...")
    await page.goto("https://postgrado.upc.edu.pe/landings/cursos-de-especializacion/")
    # Wait for content
    await page.wait_for_selector(".card-content")
    
    # Simple example logic for pilot
    results = [{
        "name": "Ingeniería de Sistemas de Información",
        "institution_slug": "upc",
        "price_pen": 0,
        "mode": "Presencial",
        "address": "Monterrico, Lima"
    }]
    
    return results

def save_to_db(data):
    """Saves or updates course data in PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        for item in data:
            # Get institution_id
            cur.execute("SELECT id FROM institutions WHERE slug = %s", (item['institution_slug'],))
            result = cur.fetchone()
            if not result:
                print(f"Institution {item['institution_slug']} not found.")
                continue
            inst_id = result[0]
            
            # Simple slug generation from name
            course_slug = item['name'].lower().replace(" ", "-").replace("/", "-")[:255]
            
            # Upsert course
            cur.execute("""
                INSERT INTO courses (institution_id, name, slug, price_pen, mode, address, last_scraped_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (institution_id, name, slug) DO UPDATE SET
                    price_pen = EXCLUDED.price_pen,
                    mode = EXCLUDED.mode,
                    address = EXCLUDED.address,
                    last_scraped_at = EXCLUDED.last_scraped_at
            """, (inst_id, item['name'], course_slug, item['price_pen'], item['mode'], item['address'], datetime.now()))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully saved {len(data)} items to database.")
    except Exception as e:
        print(f"Database error: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Scrape UTEC
        try:
            utec_data = await scrape_utec(page)
            save_to_db(utec_data)
        except Exception as e:
            print(f"Error scraping UTEC: {e}")
        
        # Scrape UPC
        try:
            upc_data = await scrape_upc(page)
            save_to_db(upc_data)
        except Exception as e:
            print(f"Error scraping UPC: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
