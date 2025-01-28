#------------------------------ IMPORTACIONES DE LIBRERIAS ------------------------------

from playwright.async_api import async_playwright, Playwright
from traffic import Traffic
from script_loaded import ScriptLoaded
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
targets = None

#------------------------------- FUNCIONES AUXILIARES ----------------------------------
def generar_timestamp():
    # Generarmos nuestro timestamp en milisegundos desde el inicio del programa
    return int((time.time() - start_time) * 1000)

async def generar_informe_json():
    # Toda la informacion recopilada la almacenamos en un JSON para su posterior analisis
    with open("report.json", "w") as report:
        json.dump(informacion_json, report, indent=4)

def create_initiator(traffic):
    initiator = traffic.get("initiator", None)
    if initiator:
        initiator_type = initiator["type"]
        if initiator_type == "parser":
            url = initiator.get("url", None)
        elif initiator_type == "script":
            script_id = initiator.get("stack", None).get("callFrames", None)[0].get("scriptId", None)
            if script_id:
                return script_id
            return initiator.get("stack", None).get("parent", None).get("callFrames", None)[0].get("scriptId", None)
        else:
            return initiator.get("url", None)
        
#------------------------------- CREACION DE NODOS ----------------------------------------

def traffic_node(traffic):
    nodo = Traffic(
        request_ID=traffic["requestId"],
        target_ID=traffic["frameId"],
        origin=traffic["request"]["url"],
        initiator=create_initiator(traffic),
        timestamp=generar_timestamp()
    )
    informacion_json.append(nodo.to_dict())

def script_node(script):
    nodo = ScriptLoaded(
        script_ID=script["scriptId"],
        target_ID=script.get("executionContextAuxData", None).get("frameId", None),
        execution_context_ID=script["executionContextId"],
        type=script.get("executionContextAuxData", None).get("type", None),
        origin=script["url"],
        initiator=create_initiator(script),
        timestamp=generar_timestamp()
    )
    informacion_json.append(nodo.to_dict())

def crear_diccionario_targets(targets: dict):
    """
    Creamos una funcion que crea un diccionario en el que la clave es la URL y el valor el targetID,
    para poder relacionar muchos de los nodos
    """
    dic_targets = {}
    targets = targets["targetInfos"]
    for target in targets:
        dic_targets[target["url"]] = target["targetId"]
    return dic_targets

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
    await cdp_sesion.send("Network.enable")
    await cdp_sesion.send("Debugger.enable")
    
    # FUNCIONES DEL EVENTO NETWORK
    cdp_sesion.on("Network.requestWillBeSent", traffic_node)

    # FUNCIONES DEL EVENTO DEBUGGER
    cdp_sesion.on("Debugger.scriptParsed", script_node)

    """----------------------- ACTIVIDADES EN EL NAVEGADOR ---------------------------"""
    # Con la pagina activa navegamos a una web
    print(f"{yellowColour}[+]{endColour}{blueColour} Realizando acciones automaticas en el navegador...{endColour}")
    await page.goto("http://cosec.inf.uc3m.es")
    
    """----------------------- CIERRE DE CONTEXTO ------------------------------------"""
    # Guardamos los targets existentes
    targets = await cdp_sesion.send("Target.getTargets")
    targets = crear_diccionario_targets(targets)

    print(f"{turquoiseColour}[+]{endColour}{blueColour} Información de los targets creados:{endColour}\n{targets}")
    
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