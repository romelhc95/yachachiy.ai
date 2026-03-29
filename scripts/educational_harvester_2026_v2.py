import asyncio
from playwright.async_api import async_playwright
import json
import os

async def scrape_site(page, url, site_name, selectors):
    print(f"Scraping {site_name} at {url}...")
    try:
        # Using wait_until="load" for faster results if networkidle is too slow
        await page.goto(url, timeout=90000, wait_until="domcontentloaded")
        
        # Give it a bit more time for dynamic content
        await asyncio.sleep(5)
        
        # Wait for some potential content
        found_selector = None
        for selector in selectors:
            try:
                # Use a shorter wait for each selector
                await page.wait_for_selector(selector, timeout=5000)
                print(f"Found selector {selector} for {site_name}")
                found_selector = selector
                break
            except:
                continue
        
        all_results = []
        if found_selector:
            elements = await page.query_selector_all(found_selector)
            for el in elements:
                try:
                    html = await el.evaluate("node => node.outerHTML")
                    text = await el.inner_text()
                    all_results.append({
                        "institution": site_name,
                        "url": url,
                        "selector": found_selector,
                        "raw_html": html,
                        "extracted_text": text
                    })
                except Exception as e:
                    print(f"Error extracting element for {site_name}: {e}")
        
        if not all_results:
            # Fallback: capture main content or body if no specific selectors found
            print(f"No specific selectors found for {site_name}, capturing main/body content.")
            main_el = await page.query_selector("main") or await page.query_selector("body")
            if main_el:
                html = await main_el.evaluate("node => node.outerHTML")
                text = await main_el.inner_text()
                all_results.append({
                    "institution": site_name,
                    "url": url,
                    "selector": "fallback",
                    "raw_html": html,
                    "extracted_text": text
                })
            
        return all_results
    except Exception as e:
        print(f"Error scraping {site_name}: {e}")
        return []

async def main():
    sites = [
        {
            "name": "PUCP",
            "url": "https://posgrado.pucp.edu.pe/programas/maestrias/",
            "selectors": [".programa-item", ".card", "article", ".programa"]
        },
        {
            "name": "UPN",
            "url": "https://www.upn.edu.pe/posgrado/maestrias",
            "selectors": [".card-posgrado", ".views-row", ".maestria-item", "article"]
        },
        {
            "name": "USMP",
            "url": "https://usmp.edu.pe/posgrado/",
            "selectors": [".program-card", ".card", ".col-lg-4", "article"]
        },
        {
            "name": "ESAN",
            "url": "https://www.esan.edu.pe/maestrias/",
            "selectors": [".card-maestria", ".item-maestria", "article", ".card"]
        },
        {
            "name": "UTEC",
            "url": "https://posgrado.utec.edu.pe/cursos-y-programas",
            "selectors": [".card1", ".card", ".program-item", "article"]
        }
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Randomize user agent slightly
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        all_data = []
        for site in sites:
            try:
                site_results = await scrape_site(page, site["url"], site["name"], site["selectors"])
                all_data.extend(site_results)
            except Exception as e:
                print(f"Failed to scrape {site['name']}: {e}")
        
        await browser.close()
        
        output_file = "C:/xampp/htdocs/yachachiy_ai/scripts/scraped_courses_2026_v2.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully scraped {len(all_data)} items and saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
