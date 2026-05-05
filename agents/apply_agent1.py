# trying to not use AI as much as humanly possivle
"""
    1. we are going to start the browser
    2. we are going to go to the page
    3. we are going to look through all the links and find the one with apply
    4. click the link
    5. we are going to wait for everything to load
    6. after everything loads we are going to look for apply manually link
    7. once we click the apply manually we are going to again wait for the new page to load
    8. after everything loads we are going to click the sign in button
    9. that will be the same exact page and now we are going to try to print the spam content
    10. we are going to fill out the email and password and the click sign in
"""

import asyncio
from playwright.async_api import async_playwright, Playwright
from playwright.sync_api import sync_playwright

url = "https://www.allstate.jobs/job/23127059/product-engineer-java-spring-boot-w-full-stack-option-remote-il/?source=LinkedInJB&utm_source=LILimitedListings&source=linkedinjobpostings"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        print(page.title())
        link = page.locator("a").all()
        for l in link:
            text = l.text_content().lower().strip()
            print(text)
            if "apply" in text:
                with page.expect_popup() as new_page:
                    l.click()
                new_page = new_page.value
                new_page.wait_for_load_state("networkidle")
                break
        print(new_page.url)
        new_page.wait_for_timeout(5000)
        link1 = new_page.locator("a").all()
        for l in link1:
            text = l.text_content().lower().strip()
            print(text)
        button = new_page.locator("button").all()
        for b in button:
            text = b.text_content().lower().strip()
            print(text)
            if "accept" in text:
                b.click()
                break
        link2 = new_page.locator("a").all()
        for l in link2:
            text = l.text_content().lower().strip()
            print(text)
            if "apply" in text:
                l.click()
                break
        print(new_page.url)
        new_page.wait_for_load_state("networkidle")
        new_page.wait_for_timeout(5000)
        label = new_page.locator("label").locator("span").all()
        for l in label:
            text = l.text_content()
            print(text)
        button = new_page.locator("button").all()
        i = 0
        for b in button:
            text = b.text_content().lower()
            if "sign in" in text:
                if i == 0:
                    i += 1
                    continue
                b.click()
                break
            print(text)
                
        print(new_page.url)
        new_page.wait_for_timeout(5000)
        label = new_page.locator("label").locator("span").all()
        print("-------")
        for l in label:
            text = l.text_content().lower()
            print(text)
        browser.close()

main()
print("Hello World")