"""
AUTOR: David Martín Castro
This script contains the main function, which is used to run the program.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

# External modules
import asyncio
from playwright.async_api import async_playwright, Playwright

# Own modules
import paths
import utils.fileUtils as fileUtils
import utils.timeUtils as timeUtils
import utils.cdpUtils as cdpUtils
from webGraph import create_graph
from colours import *

#------------------------- PREVIOUS INFORMATION DELETION -----------------

print(f"{greenColour}[+]{endColour}{grayColour} Deleting previous information...{endColour}")
fileUtils.remove_report()
fileUtils.remove_user_data()

#------------------------------ MAIN FUNCTION ----------------------------

print(f"{greenColour}[+]{endColour}{grayColour} Starting program...{endColour}")
# Start time of the program
timeUtils.start_time = timeUtils.get_current_time()


async def run(playwright: Playwright, extension_path: str) -> None:

    # Descompress the extension
    fileUtils.decompress_extension(extension_path)
    # Create a new browser context
    context = await playwright.chromium.\
        launch_persistent_context(paths.get_user_data_path(), headless=False, \
        args=[f"--disable-extensions-except={paths.get_extension_path()}",\
        f"--load-extension={paths.get_extension_path()}"])
    
    # We will use the first page created by the browser context
    page = context.pages[0]

    # Create a new CDP (Chrome DevTools Protocol) session
    cdp_session = await context.new_cdp_session(page)

    # Enable the events that we want to capture
    await cdpUtils.enable_events(cdp_session)

    # Set the breakpoints needed
    await cdpUtils.set_breakpoints(cdp_session)
    # Event listener events
    await cdpUtils.event_listener_events(cdp_session)
    async def api_call_detected(api_name):
        cdpUtils.apiCallName = api_name
        
    # Expose the api_call_detected, so it can be called from hooks.js
    await context.expose_function("pyNotify", api_call_detected)
    # Read the javascript file where the proxy is defined
    with open("hooks.js", "r", encoding="utf-8") as file:
            hooks = file.read()
    # Add the proxy and hooks to the context
    await context.add_init_script(hooks)

    # Handler for reconfiguration of the CDP session after a navigation
    async def on_frame_navigated(frame):
        if frame == page.main_frame:
                await cdpUtils.enable_events(cdp_session)
                await cdpUtils.set_breakpoints(cdp_session)
                await cdpUtils.event_listener_events(cdp_session)
                await context.add_init_script(hooks)
    
    # Calling get_targets at the beginning of the program
    targets = await cdp_session.send("Target.getTargets")
    cdpUtils.get_targets(targets)

    # Call CDP functions
    cdpUtils.target_events(cdp_session)
    cdpUtils.page_events(cdp_session)
    cdpUtils.network_events(cdp_session)
    cdpUtils.execution_context_events(cdp_session)
    cdpUtils.script_events(cdp_session)
    cdpUtils.DOM_events(cdp_session)
    cdpUtils.paused_events(cdp_session)

    page.on("framenavigated", on_frame_navigated)

    # Navigation activities
    await page.goto("http://127.0.0.1")

    # Browser context closing
    await page.wait_for_event("close", timeout=0)
    # We used a try to avoid errors when closing the context
    try:
        # Wait for all processes to close
        await asyncio.sleep(2)
        await context.close()
    except Exception as e:
        print(f"{yellowColour}[!]{endColour}{grayColour}{e}{endColour}")

    # Delete user data
    fileUtils.remove_user_data()

    # Generation of the json report
    await cdpUtils.generate_json_report()

    # Remove the extension
    fileUtils.remove_extension()

    # Generation of Web Graph
    print(f"{greenColour}[+]{endColour}{grayColour} Creating Web Graph...{endColour}")
    create_graph(cdpUtils.report_json)
    print(f"{greenColour}[+]{endColour}{grayColour} Web Graph finished{endColour}")
    

    print(f"{greenColour}[+]{endColour}{grayColour} Program finished{endColour}")

#--------------------------- MAIN FUNCTION CALL --------------------------

async def main(extension_path: str):
    async with async_playwright() as playwright:
        await run(playwright, extension_path)