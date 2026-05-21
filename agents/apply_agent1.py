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
from playwright_stealth import Stealth
import random


url = "https://www.allstate.jobs/job/23213905/-net-software-engineer-lead-consultant-lpi-lender-placed-insurance-tracking-remote/?_gl=1*18gc4vh*_ga*OTI2NTIyMTI3LjE3NzkzMTQxODk.*_ga_E5RN65WV3V*czE3NzkzMTQxODgkbzEkZzAkdDE3NzkzMTQxOTEkajU3JGwwJGgw"

def main():
    with Stealth().use_sync(sync_playwright()) as p:
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
        robot_words = ["robot only"]
        fields = []
        submit = new_page.locator('[data-automation-id="click_filter"][aria-label="Sign In"]')
        span = new_page.locator("label").locator("span").all()
        for s in span:
            text = s.text_content().strip()
            if text in robot_words:
                continue
            print(text)

        input = new_page.locator("input").all()
        for i in input:
            input_id = i.get_attribute("id")
            types = i.get_attribute("type")
            if not input_id:
                continue
            if len(input_id) > 15:
                continue
            update = {
                "question": None,
                "type": types,
                "input_id": input_id
            }
            fields.append(update)

        label = new_page.locator("label").all()
        for l in label:
            input_id = l.get_attribute("for")
            text = l.text_content().strip()
            if not input_id:
                continue
            if len(input_id) > 15:
                continue
            for field in fields:
                if field["input_id"] == input_id:
                    field["question"] = text
                    break

        new_page.wait_for_timeout(7000)
        new_page.locator(f"#{fields[0]['input_id']}").press_sequentially("peytonrivers716@gmail.com", delay=random.randint(100,200))
        new_page.locator(f"#{fields[1]['input_id']}").press_sequentially("Bprivers1!", delay=random.randint(100,200))
        submit.click()
        new_page.wait_for_load_state("networkidle")
        new_page.wait_for_selector("input")
        new_page.wait_for_timeout(10000)
        print(fields)
        print(new_page.url)
        step_label = new_page.locator('[aria-live="polite"]:has-text("current step")').text_content().strip()
        print(step_label)

        current, total = step_label.lower().replace("current step ", "").split(" of ")
        current = int(current)
        total = int(total)

        input = new_page.locator("input").all()
        print(input)
        field1 = []
        for i in input:
            input_id = i.get_attribute("id")
            print(input_id)
            type = i.get_attribute("type")
            if not input_id:
                continue
            first_letter = input_id[0]
            print(first_letter)
            if first_letter.isdigit():
                continue
            update = {
                "question": None,
                "answer": None,
                "type": type,
                "input_id": input_id
            }
            field1.append(update)

        label = new_page.locator("label").all()
        for l in label:
            text = l.text_content().strip()
            input_id = l.get_attribute("for")
            if not input_id:
                continue
            print(input_id)
            first_letter = input_id[0]
            print(first_letter)
            if first_letter.isdigit():
                continue
            for field in field1:
                if field["input_id"] == input_id:
                    field["question"] = text
                    break
        print(field1)
        for field in field1:
            if field['type'] == 'text':
                new_page.locator(f"#{field['input_id']}").press_sequentially("Peyton", delay=random.randint(100,200))
                field["answer"] = "Peyton"
        print("-----------")
        button = new_page.locator("button").all()
        button_questions = []
        for b in button:
            dropdown = b.get_attribute("aria-haspopup")
            print(dropdown)
            if dropdown != "listbox" and dropdown != "true":
                continue
            button_id = b.get_attribute("id")
            update = {
                "question": None,
                "answer": None,
                "button_id": button_id
            }
            button_questions.append(update)
        
        label = new_page.locator("label").all()
        for l in label:
            button_id = l.get_attribute("for")
            if not button_id:
                continue
            text = l.text_content()
            for b in button_questions:
                if b["button_id"] == button_id:
                    b["question"] = text
                    break

        button_questions = [b for b in button_questions if b["question"] is not None]
        print(button_questions)

        for b in button:
            text = b.text_content().strip()
            print(text)
            if text.lower() == "save and continue":
                continue_id = b.get_attribute("data-automation-id")
                break
        print("----- continue id")
        print(continue_id)

        button_values = {
            "country--country": "United States of America",
            "address--countryRegion": "North Carolina",
            "phoneNumber--phoneType": "Mobile"
        }

        for b in button_questions:
            value = button_values.get(b["button_id"])
            if not value:
                continue
            new_page.locator(f"#{b['button_id']}").click()
            new_page.get_by_role("option", name=value, exact=True).click()
            b["answer"] = value
        new_page.locator(f'[data-automation-id="{continue_id}"]').click()
        field1 = [f for f in field1 if f["question"] is not None]
        print(field1)
        print("------------")
        print(button_questions)
        new_page.wait_for_timeout(7000)
        browser.close()

main()