import asyncio, shutil
from playwright.async_api import async_playwright, Playwright

# Guardamos la dirección de la extensión
path_to_extension = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/Postman-Interceptor-Chrome-Web-Store"
# Este será el path en el que amacenamos toda la informacion del usuario (contexto permanente)
user_data_path = "C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_path"

#URLs que se filtran para no sobrecargar de informacion innecesaria
url_filtradas = ["google-analytics", "gstatic", "apis.google.com", "play.google.com"]

# Esta función permite imprimir las peticiones que se realicen desde nuestro contexto
def mostrar_peticiones(request):
    # Si la peticion no contiene ningun contenido de las url que filtramos entonces las imprimimos
    if not any(url in request.url for url in url_filtradas):
        print(f"REQUEST: {request.method} {request.url}")

# Esta función permite imprimir las respuestas que se reciben en nuestro contexto
def mostrar_respuestas(response):
     # Si la respuesta no contiene ningun contenido de las url que filtramos entonces las imprimimos
    if not any(url in response.url for url in url_filtradas):
        print(f"RESPONSE: {response.status} {response.url}")

# Función principal donde ocurre el hilo de creación de contexto, carga de extensiones,...
async def run(playwright:Playwright):
    # Creamos ocontexto y además cargamos en el una extensión
    chromium = playwright.chromium
    context = await chromium.launch_persistent_context(user_data_path, headless=False, args=[f"--disable-extensions-except={path_to_extension}", f"--load-extension={path_to_extension}"])
    page = context.pages[0]
    
    # Captamos las peticiones enviadas y respuestas recibidas por el servidor
    context.on("request", mostrar_peticiones)
    context.on("response", mostrar_respuestas)

    # Esperamos 300 segundos a terminar la ejecución del programa
    await page.wait_for_event("close", timeout=0)
    await context.close()
    # Eliminamos el directorio donde almacenamos la información del usuario en caso de no necesitarla.
    shutil.rmtree("C:/Users/david/OneDrive/Escritorio/UC3M/TFG/user_data_path")

# Función para poder ejecutar todo el programa
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
