import asyncio
from playwright.async_api import async_playwright

async def run():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            print("Playwright OK")
            await browser.close()
    except Exception as e:
        print(f"Playwright ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run())
