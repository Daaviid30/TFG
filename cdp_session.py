from playwright.async_api import async_playwright, Playwright
import asyncio


async def run(playwright: Playwright):
    context = await playwright.chromium.launch(headless=False)
    page = await context.new_page()

    # Abro un cliente para comunicarme con el CDP
    client = await page.context.new_cdp_session(page)

    # Habilitamos el modo de red en CDP
    await client.send("Network.enable")

    # Con CDP rastramos el trafico generado por la web
    client.on("Network.requestWillBeSent", lambda request: print(request["initiator"]["url"], request["initiator"]["type"])\
               if request["initiator"]["type"] != "other" else None)
    
    await page.goto("https://cosec.inf.uc3m.es")

    await page.wait_for_event("close", timeout=0)
    await context.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())