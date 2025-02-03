#------------------------------ IMPORTACIONES DE LIBRERIAS ------------------------------

from playwright.async_api import async_playwright, Playwright
from traffic import Traffic # Nodos de peticiones capaturadas
from script_loaded import ScriptLoaded # Nodos de scripts cargados
import asyncio, shutil, json, time, os
import navigation_graph # Script donde se crea el grafo
import networkx as nx # Libreria para grafos
import matplotlib.pyplot as plt # Mostrar el grafo

#------------------------------- ELIMINAR REPORTE Y USER DATA ANTERIOR ------------------

""" 
A la hora de crear un contexto permanente para poder cargar la extensión, necesitamos un directorio
donde almacenar datos del usuario, por ello en cada ejecución borramos los datos anteriores.
"""

try:
    os.remove("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/report.json")
except:
    print("No existen reportes anteriores")

try:
    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir")
except:
    print("No existen directorios con datos de usuarios anteriores")
#------------------------------- PALETA DE COLORES --------------------------------------

"""
Paleta de colores para mostrar la salida de forma más visual
"""
greenColour = "\033[0;32m\033[1m" 
endColour = "\033[0m\033[0m" 
redColour = "\033[0;31m\033[1m" 
blueColour = "\033[0;34m\033[1m" 
yellowColour = "\033[0;33m\033[1m" 
purpleColour = "\033[0;35m\033[1m" 
turquoiseColour = "\033[0;36m\033[1m" 
grayColour = "\033[0;37m\033[1m"

#------------------------------- VARIABLES GLOBALES -------------------------------------

# Path donde almacenamos datos de usuario y directorio de la extensión
user_data_dir = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_dir"
path_to_extension = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/Postman-Interceptor-Chrome-Web-Store"
# Tiempo de inicio de ejecución del programa para crear timestamps
start_time = time.time()
# Información de los nodos almacenados en forma de diccionario para crear un JSON
informacion_json = []
# Información de los nodos almacenados en forma de objetos
nodos = []
# Variable en la que almacenaremos informacion de los targets y contextos de ejecución
targets = None
execution_contexts = {}

#------------------------------- FUNCIONES AUXILIARES ----------------------------------

def generar_timestamp():
    # Generarmos nuestro timestamp en milisegundos desde el inicio del programa
    return int((time.time() - start_time) * 1000)

async def generar_informe_json():
    # Toda la informacion recopilada la almacenamos en un JSON para su posterior analisis
    with open("report.json", "w") as report:
        json.dump(informacion_json, report, indent=4)

"""
Creamos la siguiente función para poder diferenciar y obtener diferentes initiators de
peticiones realizadas, todos desde el objeto Initiator (si es que existe).
"""
def create_network_initiator(traffic):
    initiator = traffic.get("initiator", None)
    if initiator:
        initiator_type = initiator["type"]
        if initiator_type == "parser":
            url = initiator.get("url", None)
            return url
        elif initiator_type == "script":
            script_id = initiator.get("stack", None).get("callFrames", None)[0].get("scriptId", None)
            if script_id:
                return script_id
            return initiator.get("stack", None).get("parent", None).get("callFrames", None)[0].get("scriptId", None)
        else:
            return initiator.get("url", traffic["documentURL"])
    return traffic["documentURL"]
        
"""
Mismo objetivo que la función anterior, con la diferencia de que aquí el initiator es de un script
cargado y se realiza la busqueda desde el objeto stackTrace.
"""
def create_script_initiator(script):
    stack_trace = script.get("stackTrace", None)
    if stack_trace:
        callframe = stack_trace.get("callFrames", None)[0]
        return callframe.get("scriptId", None)
    return execution_contexts[script["executionContextId"]][0]

"""
Creamos una funcion que crea un diccionario en el que la clave es la URL y el valor el targetID,
para poder relacionar muchos de los nodos
"""     
def crear_diccionario_targets(targets: dict):
    dic_targets = {}
    targets = targets["targetInfos"]
    for target in targets:
        dic_targets[target["url"]] = target["targetId"]
    return dic_targets

"""
Función que cambia los initiators si la url de los nodos coincide con un ID especifico.
[NO ESTA EN USO]
"""
def transformar_target(nodos: list, dic_targets: dict):
    for nodo in nodos:
        if nodo.initiator and nodo.initiator in dic_targets.keys():
            nodo.initiator = dic_targets[nodo.initiator]

""" 
Almacenamos la información de los contextos de ejecución por si los necesitamos 
mas adelante a la hora de crear lo initiators.
{executionContextId: [name, origin]}
"""        
def execution_context_info(execution_context):
    
    context = execution_context["context"]
    id = context["id"]
    if context.get("auxData", None).get("isDefault", None):
        name = "default"
    else:
        name = context["name"]
    origin = context["origin"]
    execution_contexts[id] = [name, origin]

#------------------------------- CREACION DE NODOS ----------------------------------------

"""
Declaramos y creamos objetos de nodos de tráfico según vamos capturando peticiones
realizadas.
"""
def traffic_node(traffic):
    nodo = Traffic(
        request_ID=traffic["requestId"],
        target_ID=traffic["frameId"],
        url=traffic["request"]["url"],
        initiator=create_network_initiator(traffic),
        timestamp=generar_timestamp()
    )
    nodos.append(nodo)
    informacion_json.append(nodo.to_dict())

"""
Declaramos y creamos objetos de nodos de scripts según estos van siendo cargados en el contexto
que les corresponda.
"""
def script_node(script):
    nodo = ScriptLoaded(
        script_ID=script["scriptId"],
        target_ID=script.get("executionContextAuxData", None).get("frameId", None),
        execution_context_ID=script["executionContextId"],
        type=script.get("executionContextAuxData", None).get("type", None),
        origin=execution_contexts[script["executionContextId"]][1],
        initiator=create_script_initiator(script),
        timestamp=generar_timestamp()
    )
    nodos.append(nodo)
    informacion_json.append(nodo.to_dict())

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
    await cdp_sesion.send("Runtime.enable")
    
    # FUNCIONES DEL EVENTO NETWORK
    cdp_sesion.on("Network.requestWillBeSent", traffic_node)

    # FUNCIONES DEL EVENTO DEBUGGER
    cdp_sesion.on("Debugger.scriptParsed", script_node)

    # FUNCIONES PARA CAPTURAR EXECUTION CONTEXTS
    cdp_sesion.on("Runtime.executionContextCreated", execution_context_info)

    """----------------------- ACTIVIDADES EN EL NAVEGADOR ---------------------------"""
    # Con la pagina activa navegamos a una web
    print(f"{yellowColour}[+]{endColour}{blueColour} Realizando acciones automaticas en el navegador...{endColour}")
    await page.goto("http://cosec.inf.uc3m.es")
    
    """----------------------- CIERRE DE CONTEXTO ------------------------------------"""
    # Guardamos los targets existentes
    # DE MOMENTO NO LO UTILIZAMOS
    targets = await cdp_sesion.send("Target.getTargets")
    targets = crear_diccionario_targets(targets)
    transformar_target(nodos, targets)

    print(f"{turquoiseColour}[+]{endColour}{blueColour} Información de los targets creados:{endColour}\n{targets}")
    print(execution_contexts)
    
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

    return nodos

#-------------------------------- LLAMADA A LA FUNCION PRINCIPAL ------------------------------
async def main():
    async with async_playwright() as playwright:
        nodos = await run(playwright)
        grafo = navigation_graph.crear_grafo(nodos)
        nx.draw(grafo, with_labels=True, node_color="lightblue", edge_color="gray")
        plt.show()

asyncio.run(main())