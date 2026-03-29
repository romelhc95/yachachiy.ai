import asyncio
import os
import sys
from playwright.async_api import async_playwright

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.deep_crawl_yachachiy import deep_crawl_institution, upsert_courses
from api.database import SessionLocal
from api.models import Institution

async def test_uni_institution():
    db = SessionLocal()
    # Let's try UNI (Universidad Nacional de Ingeniería)
    inst = db.query(Institution).filter(Institution.slug == 'uni').first()
    db.close()
    
    if not inst:
        print("UNI not found")
        return

    print(f"Testing Deep Crawl for: {inst.name} ({inst.website_url})")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            results = await deep_crawl_institution(page, inst.id, inst.name, inst.website_url, inst.slug)
            print(f"Discovered {len(results)} courses.")
        except Exception as e:
            print(f"Error during test: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_uni_institution())
