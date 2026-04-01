import asyncio
import pytest
from playwright.async_api import async_playwright, expect

# Configuración
BASE_URL = "http://localhost:3000"

async def test_e2e_search_and_filter():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("\n[E2E] Navegando a la página principal...")
        await page.goto(BASE_URL)
        await page.wait_for_selector("article", timeout=5000)
        
        # 1. Búsqueda con un término que sabemos que existe
        print("[E2E] Probando búsqueda con 'Maestría'...")
        search_input = page.locator("input[placeholder*='estudiar']")
        await search_input.fill("Maestría")
        await page.wait_for_timeout(2000)
        
        courses = page.locator("article")
        count = await courses.count()
        print(f"[E2E] Resultados para 'Maestría': {count}")
        assert count > 0, "Debería haber al menos un resultado para 'Maestría'"
        
        # 2. Filtrado por categoría
        print("[E2E] Probando filtrado por categoría 'Maestría'...")
        await page.click("button:has-text('Maestría')")
        await page.wait_for_timeout(1000)
        
        # 3. Comparador
        print("[E2E] Probando comparador...")
        compare_buttons = page.locator("button:has-text('+ Comparar')")
        if await compare_buttons.count() > 0:
            await compare_buttons.first.click()
            print("[E2E] Primer curso añadido al comparador.")
            
            # Verificar barra flotante (más específico para evitar ambigüedad)
            floating_bar = page.locator("div.fixed").filter(has_text="seleccionados").first
            await expect(floating_bar).to_be_visible()
            
            # Navegar a comparativa
            print("[E2E] Navegando a la página de comparativa...")
            await floating_bar.locator("button:has-text('Comparar ahora')").click()
            await page.wait_for_url("**/compare**", timeout=5000)
            print(f"[E2E] Navegación a comparativa OK: {page.url}")
        else:
            print("[E2E] ERROR: No se encontraron botones de comparar.")
            assert False, "No se encontraron botones de comparar"

        await browser.close()

async def test_form_validation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL)
        
        print("\n[FORM] Probando validación de formulario de leads...")
        
        # Abrir modal de recomendación
        await page.click("button:has-text('Quiero mi recomendación')")
        await page.wait_for_selector("form", timeout=2000)
        
        # Intentar enviar vacío (validación nativa de HTML5)
        submit_btn = page.locator("button[type='submit']")
        await submit_btn.click()
        
        # Verificar que el formulario NO se envió (no aparece mensaje de éxito)
        success_msg = page.locator("text=¡Solicitud recibida!")
        await expect(success_msg).not_to_be_visible()
        
        # Probar email inválido
        print("[FORM] Probando email inválido...")
        await page.fill("input[placeholder='Ej: Juan']", "Test User")
        await page.fill("input[placeholder='Ej: Pérez']", "Test Lastname")
        await page.fill("input[type='email']", "email-invalido")
        await page.fill("input[placeholder*='987']", "999888777")
        await submit_btn.click()
        await expect(success_msg).not_to_be_visible()
        
        print("[FORM] Validación de campos OK.")
        await browser.close()

async def test_regression_accents_and_slugs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL)
        await page.wait_for_selector("article", timeout=5000)
        
        print("\n[REGRESIÓN] Probando búsqueda con acentos ('economia')...")
        search_input = page.locator("input[placeholder*='estudiar']")
        
        # Buscar 'economia' (sin acento)
        await search_input.fill("economia")
        await page.wait_for_timeout(2000)
        
        # Obtener textos de los resultados
        results = page.locator("article h3")
        count = await results.count()
        print(f"[REGRESIÓN] Encontrados {count} resultados para 'economia'")
        
        found = False
        for i in range(count):
            text = await results.nth(i).inner_text()
            print(f"  Resultado {i+1}: {text}")
            if "Economía" in text or "economia" in text.lower():
                found = True
        
        print(f"[REGRESIÓN] ¿Encontró 'Economía' buscando 'economia'?: {'SÍ' if found else 'NO'}")
        
        # Si falló, intentar de nuevo pero con 'Todos' explícito
        if not found:
            print("[REGRESIÓN] Reintentando con categoría 'Todos'...")
            await page.click("button:has-text('Todos')")
            await page.wait_for_timeout(1000)
            results = page.locator("article h3")
            count = await results.count()
            for i in range(count):
                text = await results.nth(i).inner_text()
                if "Economía" in text or "economia" in text.lower():
                    found = True
                    break
        
        assert found, "La normalización de acentos en búsqueda falló"
        
        # Probar accesibilidad de slug
        print("[REGRESIÓN] Probando accesibilidad de slug detallado...")
        detail_link = page.locator("a:has-text('Ver detalle')").first
        href = await detail_link.get_attribute("href")
        print(f"[REGRESIÓN] Navegando a slug: {href}")
        await detail_link.click()
        await page.wait_for_url(f"**{href}")
        
        # Verificar que no es 404
        h1 = page.locator("h1")
        await expect(h1).to_be_visible()
        print(f"[REGRESIÓN] Página de detalle cargada OK: {await h1.inner_text()}")
            
        await browser.close()

async def test_accessibility_ux():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL)
        
        print("\n[ACCESIBILIDAD/UX] Verificando elementos básicos...")
        
        # Header y Footer
        await expect(page.locator("header")).to_be_visible()
        await expect(page.locator("footer")).to_be_visible()
        print("[ACCESIBILIDAD/UX] Header y Footer visibles.")
        
        # Verificar que los enlaces principales funcionan (scroll-mt)
        await page.click("text=Cómo Funciona")
        await page.wait_for_timeout(500)
        await expect(page.locator("#como-funciona")).to_be_visible()
            
        print("[ACCESIBILIDAD/UX] Estructura básica OK.")
        await browser.close()

async def run_all():
    print("Iniciando batería de pruebas integrales de calidad...")
    try:
        await test_e2e_search_and_filter()
        await test_form_validation()
        await test_regression_accents_and_slugs()
        await test_accessibility_ux()
        print("\n=== TODAS LAS PRUEBAS COMPLETADAS CON ÉXITO ===")
    except Exception as e:
        print(f"\n!!! ERROR DURANTE LAS PRUEBAS: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_all())
