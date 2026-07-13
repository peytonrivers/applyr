"""
Screenshot-Only AI Application Flow

This version removes HTML/body-text extraction and relies entirely on screenshots.

Flow:
1. Open the page.
2. Wait for it to finish loading.
3. Capture a screenshot.
4. Send the screenshot to the LLM.
5. The LLM returns:
    - page_type
    - click coordinates (if needed)
    - reasoning
6. Click the returned coordinates.
7. Wait for the page to load.
8. Repeat until:
    - forms
    - signup
    - verification
    - error
9. For forms:
    - Screenshot the page.
    - Ask the AI what action to perform.
    - AI returns one action at a time:
        * click
        * type
        * scroll
        * upload resume
        * upload cover letter
        * screenshot again
        * submit
10. Continue until the application is complete.

Core Philosophy
---------------
Everything is driven by screenshots.
No DOM parsing.
No HTML extraction.
No body text.
No element collection.
The model navigates entirely from visual context.

Suggested helper functions:

wait_until_page_ready(page)

capture_screenshot(page) -> base64

ai_page_decision(screenshot)

ai_form_action(screenshot)

click_coordinates(page, x, y)

type_text(page, text)

scroll_page(page)

upload_file(page, path)

main_loop(state)
"""

import base64
import time

def capture_screenshot(page):
    screenshot = page.screenshot(full_page=False)
    return base64.b64encode(screenshot).decode("utf-8")


def screenshot_loop(state):
    page = state["current_page"]["page"]

    while True:
        page.wait_for_load_state("networkidle")

        screenshot = capture_screenshot(page)

        # Send screenshot to GPT
        # response = ai_page_decision(screenshot)

        # Expected response:
        # {
        #   "action": "click" | "type" | "scroll" | "submit" | "done",
        #   "x": 0,
        #   "y": 0,
        #   "text": "",
        #   "reason": ""
        # }

        break
