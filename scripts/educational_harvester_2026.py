import asyncio
from playwright.async_api import async_playwright
import json
import os

async def scrape_site(page, url, site_name, selectors):
    print(f"Scraping {site_name} at {url}...")
    try:
        await page.goto(url, timeout=60000, wait_until="networkidle")
        # Wait for some potential content
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=10000)
                print(f"Found selector {selector} for {site_name}")
                break
            except:
                continue
        
        # Capture all elements that match the selectors
        all_results = []
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                for el in elements:
                    html = await el.outer_html()
                    text = await el.inner_text()
                    all_results.append({
                        "institution": site_name,
                        "url": url,
                        "selector": selector,
                        "raw_html": html,
                        "extracted_text": text
                    })
                break # If we found elements with this selector, we stop looking for others for this site
        
        if not all_results:
            # Fallback: capture main content or body if no specific selectors found
            print(f"No specific selectors found for {site_name}, capturing body content.")
            body_content = await page.inner_html("body")
            all_results.append({
                "institution": site_name,
                "url": url,
                "selector": "body",
                "raw_html": body_content,
                "extracted_text": await page.inner_text("body")
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
            "selectors": [".programa-item", ".card", ".programa", "article"]
        },
        {
            "name": "UPN",
            "url": "https://www.upn.edu.pe/posgrado/maestrias",
            "selectors": [".views-row", ".card", ".maestria-item", "article"]
        },
        {
            "name": "USMP",
            "url": "https://usmp.edu.pe/posgrado/",
            "selectors": [".program-card", ".card", ".col-lg-4", "article"]
        },
        {
            "name": "ESAN",
            "url": "https://www.esan.edu.pe/maestrias/",
            "selectors": [".card-maestria", ".item-maestria", ".card", "article"]
        },
        {
            "name": "UTEC",
            "url": "https://posgrado.utec.edu.pe/cursos-y-programas",
            "selectors": [".card1", ".card", ".program-item", "article"]
        }
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        all_data = []
        for site in sites:
            site_results = await scrape_site(page, site["url"], site["name"], site["selectors"])
            all_data.extend(site_results)
        
        await browser.close()
        
        # Save results to a JSON file
        with open("C:/xampp/htdocs/yachachiy_ai/scripts/scraped_courses_2026.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully scraped {len(all_data)} items and saved to scripts/scraped_courses_2026.json")

if __name__ == "__main__":
    asyncio.run(main())
