import asyncio
from playwright.async_api import async_playwright, Playwright, Page

async def page_screenshoot(page: Page, url: str, path_screenshoot: str):
    await page.goto(url)
    await page.screenshot(path=path_screenshoot)

async def run(playwright: Playwright):
    # Select chromium as browser
    chromium = playwright.chromium
    # Launch the browser and select headless mode as False (This allows us to see the browser display)
    browser = await chromium.launch(headless=False)
    # Once we have the browser, create two different contexts
    context1 = await browser.new_context()
    context2 = await browser.new_context()
    # Next step is to open a new page in each context
    page1 = await context1.new_page()
    page2 = await context2.new_page()
    
    # Call the functions where the screenshoot will be made
    # asyncio.gather allows us to run 2 functions at the same time
    await asyncio.gather(
        page_screenshoot(page1, "http://uc3m.es", "UC3M.png"),
        page_screenshoot(page2, "https://uax.com", "UAX.png")
    )

    # Close all the contexts and the browser that we launched before
    await context1.close()
    await context2.close()
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())

