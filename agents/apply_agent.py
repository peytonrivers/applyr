# LangGraph Agent to start the Application
"""
    1. Open the URL
    2. 404 error or Timeout
        - break & set the url to inactive
    3. Track Domain inside of url
    4. Find Apply Button
        - HTML Scraping
        - Looking for buttons as well
    5. Click Apply with playwright apply tool
        - If 404 Error or Timeout
            - break & set the url to inactive
        - If Not the same Domain
            - break & est the url to inactive
    6. Send to Recognition Tool
"""

"""
    1. Grab url and open it
"""

import asyncio 
from playwright.sync_api import sync_playwright, Playwright
from playwright.async_api import async_playwright

async def grab_and_open_url():
    # 1. Retrieve url
    url = "https://www.allstate.jobs/job/23127059/product-engineer-java-spring-boot-w-full-stack-option-remote-il/?source=LinkedInJB&utm_source=LILimitedListings&source=linkedinjobpostings"
    # 2. Open the url with playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        print(await page.title())
        apply_button = None
        await button = page.locator("button").all()
        for b in button:
            if "apply" in b.inner_text().lower() and button.is_visible():
                print("it worked")
        for button in page.locator("button").all() :
            if "apply" in button.inner_text().lower() and button.is_visible():
                apply_button = button
                print("it worked!")
                break
        if not apply_button:
            for link in page.locator("a").all():
                text = link.inner_text().lower().strip()
                href = (link.get_attribute("href") or "").lower()
                if link.is_visible() and "apply now" in text and "workday" in href:
                    apply_button = link
                    break
        if apply_button:
            with page.expect_popup() as popup_info:
                apply_button.click()
            new_page = popup_info.value
            new_page.wait_for_load_state("networkidle")
            new_page.wait_for_selector("button")
            try:
                new_page.locator("button", has_text="accept cookies").click()
                new_page.wait_for_load_state("networkidle")
                new_page.wait_for_selector("[data-automation-id='applyManually']")
            except:
                print("nothing")
                pass

            print(new_page.title())
            print(new_page.url)
            for span in new_page.locator("label span").all():
                text = (span.text_content() or "").strip()
                if text:
                    print(text)
            print("---------")
            for button in new_page.locator("button").all():
                text = button.inner_text().lower().strip()
                print(text)
                if "sign in" in text.lower():
                    button.click()
                    new_page.wait_for_load_state("networkidle")
                    await new_page.wait_for_load_state("label span")
                    break
            print(new_page.url)
            print("-----------")
            for inputt in new_page.locator("label span").all():
                print(inputt.get_attribute("data-automation-id") or inputt.get_attribute("type") or "unknown")
            print("----------")
            for label in new_page.locator("label span").all():
                text = (label.text_content() or "").strip()
                print(text)
        await browser.close()

asyncio.run(grab_and_open_url())