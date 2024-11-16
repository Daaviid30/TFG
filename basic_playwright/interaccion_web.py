import asyncio
from playwright.async_api import async_playwright, Playwright

user_data_path = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_path"

async def run(playwright: Playwright):
    context = await playwright.chromium.launch(headless=False)
    page = await context.new_page()
    await page.goto("https://www.uc3m.es")
    await page.get_by_role("link", name="Aula Global").click()
    await page.get_by_text("Google").click()
    await page.get_by_label("Correo electrónico o teléfono").fill("100472099@alumnos.uc3m.es")
    await page.get_by_text("Siguiente").click()
    await page.get_by_role("textbox", name="Introduce tu contraseña").fill("")
    await page.locator(".VfPpkd-dgl2Hf-ppHlrf-sM5MNb").get_by_text("Siguiente").click()

    await page.wait_for_event("close", timeout=0)
    await context.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main()) 