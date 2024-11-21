from playwright.async_api import async_playwright, Playwright
import asyncio, shutil, json

user_data_path = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_path"

trafico_red = []

def guardar_peticiones(request):
    peticion = {
        "tipo": "REQUEST",
        "url": request.url,
        "method": request.method,
        "headers": dict(request.headers),
        "body": request.post_data or None
    }
    trafico_red.append(peticion)

def guardar_respuestas(response):
    respuesta = {
        "tipo": "RESPONSE",
        "url": response.url,
        "status": response.status,
        "headers": dict(response.headers),
    }
    trafico_red.append(respuesta)

async def run(playwright: Playwright):
    context = await playwright.chromium.launch_persistent_context(user_data_path, headless= False)
    page = context.pages[0]

    context.on("request", guardar_peticiones)
    context.on("response", guardar_respuestas)

    await page.goto("https://cosec.inf.uc3m.es")


    await page.wait_for_event("close", timeout=0)
    await context.close()
    # Eliminamos el directorio donde almacenamos la información del usuario en caso de no necesitarla.
    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_path")
    
    # Guardamos el trafico de red captado en un json
    with open("trafico_red.json", "w") as f:
        json.dump(trafico_red, f, indent=4)

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())