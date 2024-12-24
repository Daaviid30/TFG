#------------------------------ IMPORTACIONES DE LIBRERIAS ------------------------------

from playwright.async_api import async_playwright, Playwright
import asyncio, shutil, json, time, os

#------------------------------- ELIMINAR REPORTE Y USER DATA ANTERIOR ------------------
try:
    os.remove("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/report.json")
except:
    pass

try:
    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir")
except:
    pass
#------------------------------- PALETA DE COLORES --------------------------------------
greenColour = "\033[0;32m\033[1m" 
endColour = "\033[0m\033[0m" 
redColour = "\033[0;31m\033[1m" 
blueColour = "\033[0;34m\033[1m" 
yellowColour = "\033[0;33m\033[1m" 
purpleColour = "\033[0;35m\033[1m" 
turquoiseColour = "\033[0;36m\033[1m" 
grayColour = "\033[0;37m\033[1m"

#------------------------------- VARIABLES GLOBALES -------------------------------------
user_data_dir = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir"
path_to_extension = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/Postman-Interceptor-Chrome-Web-Store"
start_time = time.time()
informacion_json = []

#------------------------------- FUNCIONES AUXILIARES ----------------------------------
def generar_timestamp():
    # Generarmos nuestro timestamp en milisegundos desde el inicio del programa
    return int((time.time() - start_time) * 1000)

async def generar_informe_json():
    # Toda la informacion recopilada la almacenamos en un JSON para su posterior analisis
    with open("report.json", "w") as report:
        json.dump(informacion_json, report, indent=4)

#------------------------------- FUNCIONES JSON ----------------------------------------
def info_target(target):
    informacion = {
        "type": "TARGET",
        "url": target["targetInfo"]["url"],
        "target_type": target["targetInfo"]["type"],
        "title": target["targetInfo"]["title"],
        "timestamp": generar_timestamp()
    }
    
    informacion_json.append(informacion)

def info_network_request(request):
    informacion = {
        "type": "REQUEST",
        "request_id": request["requestId"],
        "request_url": request["request"]["url"],
        "request_method": request["request"]["method"],
        "request_post_data": request["request"].get("postDataEntries", None),
        "initiator_url": request["initiator"].get("url", None),
        "initiator_type": request["initiator"]["type"],
        "timestamp": generar_timestamp()
    }

    informacion_json.append(informacion)

def info_network_response(response):
    informacion = {
        "type": "RESPONSE",
        "request_id": response["requestId"],
        "response_url": response["response"]["url"],
        "response_status": response["response"]["status"],
        "service_worker_response_source": response["response"].get("serviceWorkerResponseSource", None),
        "timestamp": generar_timestamp()
    }

    informacion_json.append(informacion)

def info_page_navigated(page):
    informacion = {
        "type": "PAGE",
        "frame_id": page["frame"]["id"],
        "parent_id": page["frame"].get("parentId", None),
        "page_url": page["frame"]["url"],
        "timestamp": generar_timestamp()
    }

    informacion_json.append(informacion)

def info_script(script):
    informacion = {
        "type": "SCRIPT",
        "script_id": script["scriptId"],
        "script_url": script["url"],
        "stack_trace": script.get("stackTrace", None),
        "timestamp": generar_timestamp()
    }

    informacion_json.append(informacion)

#------------------------------- FUNCION PRINCIPAL --------------------------------------
async def run(playwright: Playwright):
    # Creamos un contexto permanente para poder cargar la extension que se encuentra en path_to_extension
    contexto = await playwright.chromium.launch_persistent_context(user_data_dir, headless=False,\
                                                            args=[f"--disable-extensions-except={path_to_extension}", f"--load-extension={path_to_extension}"])
    # Utilizaremos la primera pagina creada por el contexto
    page = contexto.pages[0]

    """----------------------- CDP (Chrome DevTools Protocol) ------------------------"""
    print(f"{yellowColour}[+]{endColour}{grayColour} Empezando el analisis del comportamiento del navegador{endColour}")
    # Cargamos el CDP (Chrome DevTools Protocol), que nos servira para utilizar multiples funciones
    print(f"{yellowColour}[+]{endColour}{grayColour} Cargando CDP y sus funcionalidades...{endColour}")
    cdp_sesion = await contexto.new_cdp_session(page)
    # Habilitamos los diferentes eventos que queremos capturar
    await cdp_sesion.send("Target.setDiscoverTargets", {"discover": True})
    await cdp_sesion.send("Network.enable")
    await cdp_sesion.send("Page.enable")
    await cdp_sesion.send("Debugger.enable")

    # Usamos las funciones para recoger información y mandarla a un fichero json
    # FUNCIONES DEL EVENTO TARGET
    cdp_sesion.on("Target.targetCreated", info_target)
    cdp_sesion.on("Target.targetInfoChanged", info_target)
    
    # FUNCIONES DEL EVENTO NETWORK
    cdp_sesion.on("Network.requestWillBeSent", info_network_request)
    cdp_sesion.on("Network.responseReceived", info_network_response)

    # FUNCIONES DEL EVENTO PAGE
    #cdp_sesion.on("Page.frameNavigated", info_page_navigated)

    # FUNCIONES DEL EVENTO DEBUGGER
    cdp_sesion.on("Debugger.scriptParsed", info_script)

    """----------------------- ACTIVIDADES EN EL NAVEGADOR ---------------------------"""
    # Con la pagina activa navegamos a una web
    print(f"{yellowColour}[+]{endColour}{blueColour} Realizando acciones automaticas en el navegador...{endColour}")
    await page.goto("http://127.0.0.1")
    
    """----------------------- CIERRE DE CONTEXTO ------------------------------------"""
    # Esperamos por el cierrre de la pagina que se está utilizando
    await page.wait_for_event("close", timeout=0)
    # Cerramos el contexto (con un try para evitar algun error de cierre)
    try:
        await contexto.close()
    except Exception as e:
        print(f"{redColour}[!]Error closing context: {e}{endColour}")

    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir")
    print(f"{yellowColour}[+]{endColour}{greenColour} Analisis finalizado!{endColour}")


    """----------------------- CREACION DE REPORTE JSON ------------------------------"""
    print(f"{yellowColour}[!]{endColour}{blueColour} Generando reporte...{endColour}")
    await generar_informe_json()
    print(f"{yellowColour}[+]{endColour}{greenColour} Reporte generado exitosamente, guardado como report.json{endColour}")

#-------------------------------- LLAMADA A LA FUNCION PRINCIPAL ------------------------------
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())