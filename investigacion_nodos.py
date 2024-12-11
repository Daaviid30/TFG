from playwright.async_api import async_playwright, Playwright
import asyncio, shutil

user_data_dir = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir"
path_to_extension = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/Postman-Interceptor-Chrome-Web-Store"

def info_peticiones(request):
    print(f"{request.get('documentURL')}, {request['request']['url']}, {request['initiator'].get('url', None)}")

def info_pages(page):
    print(f"URL PAGE: {page['frame']['url']}, {page['frame']['mimeType']}")

async def run(playwright: Playwright):
    contexto = await playwright.chromium.launch_persistent_context(user_data_dir, headless=False,\
                                                            args=[f"--disable-extensions-except={path_to_extension}", f"--load-extension={path_to_extension}"])
    
    page = contexto.pages[0]

    cdp_sesion = await page.context.new_cdp_session(page)
    await cdp_sesion.send("Network.enable")
    await cdp_sesion.send("Page.enable")

    #cdp_sesion.on("Network.requestWillBeSent", info_peticiones)
    cdp_sesion.on("Page.frameNavigated", info_pages)

    await page.goto("https://cosec.inf.uc3m.es")

    await page.wait_for_event("close", timeout=0)
    try:
        await contexto.close()
    except Exception as e:
        print(f"Error closing context: {e}")

    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())