from playwright.async_api import async_playwright, Playwright
import asyncio, shutil

path_to_extension = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/Postman-Interceptor-Chrome-Web-Store"
# Este será el path en el que amacenamos toda la informacion del usuario (contexto permanente)
user_data_path = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_path"

def mostrar_initiator(request):
    # URLs a filtrar
    url_filtradas = ["google-analytics", "googletagmanager"]
    
    # Verifica si el tipo es "script" y que exista "stack" en el initiator
    if request["initiator"]["type"] == "script" and "stack" in request["initiator"]:
        call_frames = request["initiator"]["stack"].get("callFrames", [])
        
        # Recorre los callFrames y busca coincidencias
        if not any(url in frame.get("url", "") for frame in call_frames for url in url_filtradas):
            print(request["initiator"]["type"], call_frames)
    
    # Para otros tipos diferentes a "other"
    elif request["initiator"]["type"] != "other":
        print(request["initiator"].get("url", "URL no disponible"), request["initiator"]["type"])




async def run(playwright: Playwright):
    context = await playwright.chromium.launch_persistent_context(user_data_path,headless=False,\
                                                                 args=[f"--disable-extensions-except={path_to_extension}", f"--load-extension={path_to_extension}"])
    page = context.pages[0]

    # Abro un cliente para comunicarme con el CDP
    client = await page.context.new_cdp_session(page)

    # Habilitamos el modo de red en CDP
    await client.send("Network.enable")

    # Con CDP rastramos el trafico generado por la web
    client.on("Network.requestWillBeSent", mostrar_initiator)
    
    await page.goto("https://cosec.inf.uc3m.es")

    await page.wait_for_event("close", timeout=0)
    await context.close()

    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_path")


async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())