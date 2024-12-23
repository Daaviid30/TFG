#------------------------------ IMPORTACIONES DE LIBRERIAS ------------------------------

from playwright.async_api import async_playwright, Playwright
import asyncio, shutil, json, time

#------------------------------- VARIABLES GLOBALES -------------------------------------
user_data_dir = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir"
path_to_extension = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/Postman-Interceptor-Chrome-Web-Store"
start_time = time.time()

#------------------------------- FUNCIONES AUXILIARES ----------------------------------
def generar_timestamp():
    # Generarmos nuestro timestamp en milisegundos desde el inicio del programa
    return int((time.time() - start_time) * 1000)

#------------------------------- FUNCIONES JSON ----------------------------------------
def info_target(target):
    informacion = {
        "url": target["targetInfo"]["url"],
        "type": target["targetInfo"]["type"],
        "title": target["targetInfo"]["title"],
        "timestamp": generar_timestamp()
    }
    print(informacion)
#------------------------------- FUNCION PRINCIPAL --------------------------------------
async def run(playwright: Playwright):
    # Creamos un contexto permanente para poder cargar la extension que se encuentra en path_to_extension
    contexto = await playwright.chromium.launch_persistent_context(user_data_dir, headless=False,\
                                                            args=[f"--disable-extensions-except={path_to_extension}", f"--load-extension={path_to_extension}"])
    # Utilizaremos la primera pagina creada por el contexto
    page = contexto.pages[0]

    """----------------------- CDP (Chrome DevTools Protocol) ------------------------"""

    # Cargamos el CDP (Chrome DevTools Protocol), que nos servira para utilizar multiples funciones
    cdp_sesion = await contexto.new_cdp_session(page)
    # Habilitamos los diferentes eventos que queremos capturar
    await cdp_sesion.send("Target.setDiscoverTargets", {"discover": True})

    # Usamos las funciones para recoger información y mandarla a un fichero json
    # FUNCIONES DEL EVENTO TARGET
    cdp_sesion.on("Target.targetCreated", info_target)
    cdp_sesion.on("Target.targetInfoChanged", info_target)

    """----------------------- ACTIVIDADES EN EL NAVEGADOR ---------------------------"""
    # Con la pagina activa navegamos a una web
    await page.goto("https://cosec.inf.uc3m.es")

    """----------------------- CIERRE DE CONTEXTO ------------------------------------"""
    # Esperamos por el cierrre de la pagina que se está utilizando
    await page.wait_for_event("close", timeout=0)
    # Cerramos el contexto (con un try para evitar algun error de cierre)
    try:
        await contexto.close()
    except Exception as e:
        print(f"Error closing context: {e}")

    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir")


#-------------------------------- LLAMADA A LA FUNCION PRINCIPAL ------------------------------
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())