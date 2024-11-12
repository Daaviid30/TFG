import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright: Playwright):
    # Determinamos el contexto en el que abrimos el navegador
    context = await playwright.chromium.launch(headless=False)
    # Una vez que tenemos el contexto abierto, abrimos una nueva pestaña
    page = await context.new_page()
    # Creamos un script de javascript que se ejecutara antes de que cargue la nueva pestaña
    await page.add_init_script(path="pre-script.js")
    # Tras esto vamos a una nueva pestaña
    await page.goto("https://www.uc3m.es")
    # Cambiamos el fondo de color y el titulo con un script que se ejecuta tras cargar la nueva pestaña
    await page.evaluate('''() => {
        document.body.style.backgroundColor = "red";
        document.title = "Educa2";
    }''')

    await page.wait_for_event("close", timeout=0)
    await context.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())