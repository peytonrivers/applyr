from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.wait_for_timeout(4000)  # let Workday JS fully hydrate
    snapshot = page.accessibility.snapshot()
    print(snapshot)
    print(json.dumps(snapshot, indent=2))
    browser.close()