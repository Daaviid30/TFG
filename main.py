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
from utils.cdpUtils import *
from colours import *

#------------------------- PREVIOUS INFORMATION DELETION -----------------

print(f"{greenColour}[+]{endColour}{grayColour} Deleting previous information...{endColour}")
fileUtils.remove_report()
fileUtils.remove_user_data()

#------------------------------ MAIN FUNCTION ----------------------------

print(f"{greenColour}[+]{endColour}{grayColour} Starting program...{endColour}")
# Start time of the program
timeUtils.start_time = timeUtils.get_current_time()


async def run(playwright: Playwright) -> None:

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
    await enable_events(cdp_session)

    # Set the breakpoints needed
    await set_breakpoints(cdp_session)
    # Event listener events
    await event_listener_events(cdp_session)

    # Handler for reconfiguration of the CDP session after a navigation
    async def on_frame_navigated(frame):
        if frame == page.main_frame:
                await enable_events(cdp_session)
                await set_breakpoints(cdp_session)
                await event_listener_events(cdp_session)
    
    # Calling get_targets at the beginning of the program
    targets = await cdp_session.send("Target.getTargets")
    get_targets(targets)

    # Call CDP functions
    target_events(cdp_session)
    page_events(cdp_session)
    network_events(cdp_session)
    execution_context_events(cdp_session)
    script_events(cdp_session)
    DOM_events(cdp_session)
    paused_events(cdp_session)

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
    await generate_json_report()

    print(f"{greenColour}[+]{endColour}{grayColour} Program finished{endColour}")

#--------------------------- MAIN FUNCTION CALL --------------------------

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())