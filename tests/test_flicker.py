import asyncio
from playwright.async_api import async_playwright
import time

async def test_flicker():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(msg.text))
        
        requests = []
        page.on("request", lambda req: requests.append(req.url))
        
        # Intentamos acceder a un curso que debería existir o al menos gatillar el componente
        # Asumimos que el front corre en localhost:3000 si estuviera prendido, 
        # pero como no lo está, este test fallará si intenta conectar.
        # El objetivo es ver si podemos simular el entorno.
        
        print("Playwright script ready. Note: This requires the dev server running at http://localhost:3000")
        
        try:
            await page.goto("http://localhost:3000/courses/data-science-piloto", wait_until="networkidle", timeout=5000)
            
            # Esperamos un poco para ver si hay múltiples disparos
            await asyncio.sleep(5)
            
            fetch_count = len([r for r in requests if "/courses/" in r])
            print(f"Fetch count for course detail: {fetch_count}")
            
            if fetch_count > 2:
                print("POSSIBLE RELOAD LOOP DETECTED")
            else:
                print("No reload loop detected in the first 5 seconds.")
                
        except Exception as e:
            print(f"Could not connect to dev server: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_flicker())
