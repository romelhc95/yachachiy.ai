import asyncio
from playwright.async_api import async_playwright
import json
import os

async def auto_scroll(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 100;
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight || totalHeight > 10000){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)

async def scrape_site(page, url, site_name, selectors):
    print(f"Scraping {site_name} at {url}...")
    try:
        await page.goto(url, timeout=90000, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        await auto_scroll(page)
        await asyncio.sleep(2)
        
        # Specific tweaks for some sites
        if site_name == "UPN":
            # UPN might have a "Ver más" button
            try:
                load_more = await page.query_selector("text=Ver más")
                if load_more:
                    await load_more.click()
                    await asyncio.sleep(2)
            except:
                pass

        found_selector = None
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                found_selector = selector
                break
            except:
                continue
        
        all_results = []
        if found_selector:
            elements = await page.query_selector_all(found_selector)
            print(f"Found {len(elements)} items for {site_name} using {found_selector}")
            for el in elements:
                try:
                    # Check if element is visible
                    if await el.is_visible():
                        html = await el.evaluate("node => node.outerHTML")
                        text = await el.inner_text()
                        if len(text.strip()) > 20: # Avoid empty or tiny elements
                            all_results.append({
                                "institution": site_name,
                                "url": url,
                                "selector": found_selector,
                                "raw_html": html,
                                "extracted_text": text
                            })
                except Exception as e:
                    pass
        
        if not all_results:
            print(f"No specific elements found for {site_name}, capturing main container.")
            # Try to find a good container instead of the whole body
            container = await page.query_selector("main") or await page.query_selector("#content") or await page.query_selector(".content") or await page.query_selector("body")
            if container:
                html = await container.evaluate("node => node.outerHTML")
                text = await container.inner_text()
                all_results.append({
                    "institution": site_name,
                    "url": url,
                    "selector": "container_fallback",
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
            "selectors": [".listado-programas .row > div", ".programa-item", ".card-programa"]
        },
        {
            "name": "UPN",
            "url": "https://www.upn.edu.pe/posgrado/maestrias",
            "selectors": [".card-posgrado", ".views-row", ".maestria-item"]
        },
        {
            "name": "USMP",
            "url": "https://usmp.edu.pe/posgrado/",
            "selectors": [".elementor-widget-container", ".program-card", ".card"]
        },
        {
            "name": "ESAN",
            "url": "https://www.esan.edu.pe/maestrias/",
            "selectors": [".card", ".card-maestria", ".item-maestria"]
        },
        {
            "name": "UTEC",
            "url": "https://posgrado.utec.edu.pe/cursos-y-programas",
            "selectors": [".card1", ".flex.items-center.justify-between.p-\[10px\]"]
        }
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 1000}
        )
        page = await context.new_page()
        
        all_data = []
        for site in sites:
            try:
                site_results = await scrape_site(page, site["url"], site["name"], site["selectors"])
                # Limit number of items per site to avoid massive JSONs, but keep enough for parser
                all_data.extend(site_results[:50]) 
            except Exception as e:
                print(f"Failed to scrape {site['name']}: {e}")
        
        await browser.close()
        
        output_file = "C:/xampp/htdocs/yachachiy_ai/scripts/scraped_courses_2026_v3.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully scraped total {len(all_data)} items and saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
