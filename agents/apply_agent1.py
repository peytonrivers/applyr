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
from playwright.sync_api import TimeoutError
import random
import json
import time
import base64
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision

from langchain_openai import ChatOpenAI

import time
import os
from dotenv import load_dotenv
load_dotenv()



openai_key = os.getenv("OPENAI_KEY")
llm = ChatOpenAI(model="gpt-5.4-nano", temperature = 0.3, api_key=openai_key)
structured_llm = llm.with_structured_output(ClickAction)
multiple_question_llm = llm.with_structured_output(MultipleQuestion)
all_elements_llm = llm.with_structured_output(AllElements)
cookies_process_llm = llm.with_structured_output(CookiesProcess)
decide_page_llm = llm.with_structured_output(DecidePage, include_raw=True)
apply_process_llm = llm.with_structured_output(ApplyProcess)
signup_process_llm = llm.with_structured_output(SignupProcess)
forms_action_llm = llm.with_structured_output(FormsAction)

url = "https://www.allstate.jobs/job/23310874/software-engineer-product-security/"

def front_page_elements(state: ApplicationState, url):

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = browser.new_page()
        print(page)
        print("------")
        page.goto(url)
        time.sleep(5)
        url1 = page.url
        state["current_page"] = {"page": page, "url": url1, "context": context, "browser": browser}

        body_text = page.locator("body").inner_text()

        clickables = page.locator(
            """
            a,
            button,
            [type="submit"],
            [type="button"],
            [role="button"],
            [role="link"]
            """
        )

        elements = []

        elements.append({
            "body_text": body_text
        })

        for i in range(clickables.count()):
            click = clickables.nth(i)

            elements.append({
                "index": i,
                "tag": click.evaluate("el => el.tagName.toLowerCase()"),
                "text": (click.text_content() or "").strip(),
                "type": click.get_attribute("type"),
                "id": click.get_attribute("id"),
                "name": click.get_attribute("name"),
                "aria-label": click.get_attribute("aria-label"),
                "href": click.get_attribute("href")
            })

        state["front_page"] = json.dumps(elements)
        response = front_page_decision(state)
        state = click_page(response)
        print(state["current_page"])
        state1 = cookies_process(state)
        state2 = cookies_action(state1)
        state3 = decide_page(state2)
        state4 = apply_process(state3)
        state5 = apply_action(state4)

        return state

def apply_process(state: ApplicationState):
    page = state["current_page"]["page"]
    body_text = page.locator("body").inner_text() or ""

    get_all_elements(state)
    all_elements = state["all_elements"]

    screenshot_base64 = get_page_screenshot_base64(page)

    prompt = f"""
You are an AI Applicant Helper.

Your job is to look at the body text, all elements, and screenshot to find the best button/link to click to move forward in the job application.

Return application_page = False only if this page is not part of a job application flow.

Priority rules:
1. If there is "Apply Manually", choose it.
2. If there is "Apply Now", "Start Application", "Continue", "Save and Continue", or "Application", choose the best one to move forward.
3. Never choose "Apply with Resume", "Autofill with Resume", "Use Resume", or "Upload Resume" when there is a manual option.
4. Never choose "Sign In" unless signing in is required and there is no way to continue manually.
5. Never choose navigation links like Careers, Home, Job Search, Back, Cancel, or Privacy Policy.
6. Choose the element index from all_elements.

Examples:
- If the page has "Apply Manually" and "Autofill with Resume", choose "Apply Manually".
- If the page has "Apply Now", choose "Apply Now".
- If the page has "Save and Continue", choose "Save and Continue".
- If the page is not an application page, return application_page = False.

body_text:
{json.dumps(body_text, indent=2)}

all_elements:
{json.dumps(all_elements, indent=2)}
"""

    response = apply_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screenshot_base64}"
                    }
                }
            ]
        }
    ])

    application_page = response["application_page"]
    index_number = response["index_number"]
    reason = response["reason"]

    print(reason)

    state["apply_process"] = {
        "application_page": application_page,
        "index_number": index_number,
        "reason": reason
    }

    apply_action(state)

    return state

def apply_action(state: ApplicationState):
    page = state["current_page"]["page"]
    clickables = state["all_elements_clickables"]
    apply_process = state["apply_process"]

    application_page = apply_process["application_page"]
    index_number = apply_process["index_number"]

    print(application_page)
    print(index_number)

    if index_number is None or application_page == False:
        state["previous_action"] = "error"
        return state

    click = clickables.nth(index_number)
    print(click)

    try:
        with page.expect_popup(timeout=5000) as popup_info:
            click.click()

        new_page = popup_info.value
        new_page.wait_for_load_state("networkidle", timeout=5000)

        state["current_page"]["page"] = new_page
        state["current_page"]["url"] = new_page.url

    except TimeoutError:
        try:
            click.click()
            page.wait_for_load_state("networkidle", timeout=20000)

            state["current_page"]["page"] = page
            state["current_page"]["url"] = page.url

        except TimeoutError:
            state["previous_action"] = "error"
            return state

    return state

def front_page_decision(state: ApplicationState):

    front_page = state["front_page"]

    prompt = f"""
You are an AI application helper.

You will decide between these 3 options:

1. "apply"
- This is an application opening page that we need to click a tag to continue to the next page.

2. "signup"
- This page requires us to sign up, create an account, or log in before continuing.

3. "error"
- This is neither an application page nor a signup page and should be returned as an error.

We will be following the ClickAction structure.

If your choice is apply:
{{"action": "apply", "index_number": 9, "reason": "this was the button with the link that goes to the application page and its text was 'Apply Now'"}}

If your choice is signup:
{{"action": "signup", "index_number": None, "reason": "none of the buttons contained text or links leading directly to an application page and the page requires account creation or login"}}

If your choice is error:
{{"action": "error", "index_number": None, "reason": "none of the page text indicated that this was an application page or a signup page"}}

The reason can be anything you decide, but make sure it is logical and explains your decision.

When choosing "apply", return the index_number of the clickable element that should be clicked.

Here is the front page:

Front Page:
{front_page}
"""

    decision = structured_llm.invoke(prompt)

    state["ai_decision"] = decision

    print(state["ai_decision"])
    return state

def get_page_screenshot_base64(page):
    screenshot_bytes = page.screenshot(full_page=False)
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
    return screenshot_base64

def wait_until_page_ready(page, timeout=20000):
    page.wait_for_load_state("domcontentloaded", timeout=timeout)

    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except TimeoutError:
        pass

    page.wait_for_function(
        """() => document.body && document.body.innerText.trim().length > 50""",
        timeout=timeout
    )

def decide_page(state: ApplicationState):
    time.sleep(5)
    action = state.get("decide_page", {}).get("action", None)

    if action == "error":
        print("An error has occurred in one of the previous pages")
        browser = state["current_page"]["browser"]
        browser.close()
        return "error"

    page = state["current_page"]["page"]

    try:
        wait_until_page_ready(page)
    except TimeoutError:
        print("Page may not be fully ready, continuing anyway...")
        time.sleep(3)
    body_text = page.locator("body").inner_text() or ""

    get_all_elements(state)
    all_elements = state["all_elements"]

    screenshot_base64 = get_page_screenshot_base64(page)

    prompt = f"""
Your job is to look at the body text, all the elements, and the screenshot to determine what type of page this is, make sure 
you use common sense when choosing which type of page it is as well.

- apply: You choose this page if this is the opening page where we need to click apply now or start the application process.
- signup: You choose this page strictly if we are required to sign up or login before continuing or if we have to create an account.
- forms: You choose this page if there are forms to fill out like asking personal questions about the user for the user's application.
- cookies: You choose this page when there are cookies that are present that need to be accepted/continued/yes to be able to continue.
- verification: This is a verification code page and we need to retrieve numbers to verify our existence.
- other: This page needs a custom action.
- error: There is an error and we should leave.

body_text:
{json.dumps(body_text, indent=2)}

all_elements:
{json.dumps(all_elements, indent=2)}
"""

    response = decide_page_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screenshot_base64}"
                    }
                }
            ]
        }
    ])

    raw = response["raw"]
    decision = response["parsed"]

    usage = raw.response_metadata.get("token_usage", {})
    print("\nDECIDE PAGE TOKEN USAGE")
    print(f"Prompt tokens: {usage.get('prompt_tokens')}")
    print(f"Completion tokens: {usage.get('completion_tokens')}")
    print(f"Total tokens: {usage.get('total_tokens')}")

    action = decision["action"]
    action_reason = decision["action_reason"]

    state["decide_page"] = {
        "action": action,
        "action_reason": action_reason
    }

    print(state["decide_page"])
    body_text = page.locator("body").inner_text() or ""
    state["body_text"] = body_text

    return state

def decide_routing(state: ApplicationState):
    try:
        action = state["decide_page"]["action"]
        return action
    except Exception:
        return "error"
        

def click_page(state: ApplicationState):
    page = state["current_page"]["page"]
    clickables = page.locator("""
                              a,
                              button,
                              [type="submit"],
                              [type="button"],
                              [role="button"],
                              [role="link"]
                              """)
    index = state["ai_decision"]["index_number"]
    click = clickables.nth(index)
    try:
        with page.expect_popup() as new_page:
            print("this is how we do it")
            click.click()
        new_page = new_page.value
        print("this is how we do it 2")
        new_page.wait_for_load_state("networkidle")
        time.sleep(5)
        print(new_page.url)
        state["current_page"]["page"] = new_page
        state["current_page"]["url"] = new_page.url
        print(f"Current Page: {state["current_page"]["page"]}")
        print(f"Current Url: {state["current_page"]["url"]}")
        return state
    except Exception:
        print("")
        page.wait_for_load_state("networkidle")
        state["current_page"]["page"] = page
        state["current_page"]["url"] = page.url
        return state

def get_all_elements(state: ApplicationState):
    page = state["current_page"]["page"]
    interactive_elements = (
    "a[href], button, input, "
    "[role='button'], [role='link'], "
    "[role='switch'], [role='tab'], [role='menuitem'], [role='menuitemcheckbox'], "
    "[role='menuitemradio'], [role='option'], [role='combobox'], [role='slider'], "
    "[role='spinbutton'], [role='treeitem'], [role='gridcell']"
    )
    clickables = page.locator(interactive_elements)
    all_elements = []
    for i in range(clickables.count()):
        element = clickables.nth(i)
        tag = element.evaluate("el => el.tagName.toLowerCase()")
        element_type = element.get_attribute("type")
        if element_type == "radio" or element_type == "checkbox":
            continue
        index = i
        raw_text = element.text_content() or ""
        element_text = raw_text.strip()
        element_id = element.get_attribute("id")
        label_text = ""
        
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                raw_label_text = label.text_content() or ""
                label_text = raw_label_text.strip()
        element_attributes = element.evaluate("""
        el => {
                let elementAttribute = [];
                for (const attr of el.attributes) {
                    elementAttribute.push({ name: attr.name, value: attr.value });
                }
                return elementAttribute;
            }
        """)
        data = {
            "tag": tag,
            "index": index,
            "element_id": element_id,
            "text": element_text,
            "label_text": label_text,
            "element_attributes": element_attributes
        }
        all_elements.append(data)
    state["all_elements"] = all_elements
    state["all_elements_clickables"] = clickables
    return state

def ai_all_elements(state: ApplicationState):
    all_elements = state["all_elements"]
    body_text = state["body_text"]

    prompt = f"""
    Your an AI Applicant Helper on the Forms page and your job is two things. 1st is to create a custom questions grouping so what you will be doing is looking through the body text and all of the indexes with its attributes to then create a custom grouping list with the question and option that we will answer later on so do not include questions we will not answer.
    Ex: [{{'question': "what is your first name", "index": 4}}, {{'question': "What is your phone number", "index": 8}}]

    1. The second thing you will be doing is to try and find the element that saves and continues or submits the application with the reason.
    Ex: {{
        "follow_through_element": 109,
        "follow_through_reason": "it's text contained save and continue with a link to go to the next page"
    }}

    body_text: {json.dumps(body_text)}
    all_elements: {json.dumps(all_elements)}
    """

    response = all_elements_llm.invoke(prompt)
    print(response)
    presorted_data = response["custom_grouping"]
    sorted_data = sorted(presorted_data, key=lambda x: x["index"])

    tracker = 0
    final_elements = []

    for i in range(len(all_elements)):
        if tracker >= len(sorted_data):
            break

        index1 = all_elements[i]["option"][0]["index"]
        index2 = sorted_data[tracker]["index"]

        if index1 == index2:
            final_elements.append({
                "question": sorted_data[tracker]["question"],
                "option": all_elements[i]["option"]
            })
            tracker += 1

    state["all_elements"] = final_elements
    state["follow_through_element"] = response["follow_through_element"]
    state["follow_through_reason"] = response["follow_through_reason"]

    return state

def get_all_radio(state: ApplicationState):
    page = state["current_page"]["page"]
    clickables = page.locator("""[type="radio"], [role="radio"]""")
    radio_elements = []
    radio_names = []

    for i in range(clickables.count()):
        click = clickables.nth(i)

        element_data = click.evaluate("""
        el => {
            let attrs = {};
            for (const attr of el.attributes) {
                attrs[attr.name] = attr.value;
            }

            return {
                tag: el.tagName.toLowerCase(),
                element_id: attrs.id || null,
                element_type: attrs.type || null,
                role: attrs.role || null,
                aria_label: attrs["aria-label"] || null,
                name: attrs.name || null,
                placeholder: attrs.placeholder || null,
                value: attrs.value || null,
                href: attrs.href || null,
                onclick: attrs.onclick || null,
                text: el.textContent || ""
            };
        }
        """)

        name = element_data["name"]

        if name in radio_names:
            continue
        if name:
            radio_names.append(name)

        current_radio = []

        label_text = ""
        element_id = element_data["element_id"]
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.first.text_content() or ""

        data = {
            "tag": element_data["tag"],
            "index": i,
            "element_id": element_data["element_id"],
            "element_type": element_data["element_type"],
            "role": element_data["role"],
            "aria_label": element_data["aria_label"],
            "name": element_data["name"],
            "placeholder": element_data["placeholder"],
            "value": element_data["value"],
            "href": element_data["href"],
            "onclick": element_data["onclick"],
            "text": element_data["text"],
            "label_text": label_text
        }

        current_radio.append(data)

        for l in range(clickables.count()):
            if i == l:
                continue

            click2 = clickables.nth(l)

            element_data2 = click2.evaluate("""
            el => {
                let attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }

                return {
                    tag: el.tagName.toLowerCase(),
                    element_id: attrs.id || null,
                    element_type: attrs.type || null,
                    role: attrs.role || null,
                    aria_label: attrs["aria-label"] || null,
                    name: attrs.name || null,
                    placeholder: attrs.placeholder || null,
                    value: attrs.value || null,
                    href: attrs.href || null,
                    onclick: attrs.onclick || null,
                    text: el.textContent || ""
                };
            }
            """)

            name2 = element_data2["name"]

            if name != name2:
                continue

            label_text2 = ""
            element_id2 = element_data2["element_id"]
            if element_id2:
                label2 = page.locator(f'[for="{element_id2}"]')
                if label2.count() > 0:
                    label_text2 = label2.first.text_content() or ""

            data2 = {
                "tag": element_data2["tag"],
                "index": l,
                "element_id": element_data2["element_id"],
                "element_type": element_data2["element_type"],
                "role": element_data2["role"],
                "aria_label": element_data2["aria_label"],
                "name": element_data2["name"],
                "placeholder": element_data2["placeholder"],
                "value": element_data2["value"],
                "href": element_data2["href"],
                "onclick": element_data2["onclick"],
                "text": element_data2["text"],
                "label_text": label_text2
            }

            current_radio.append(data2)

        radio_elements.append({
            "grouping": name,
            "question": None,
            "options": current_radio
        })

    state["radio_elements"] = radio_elements
    state["radio_elements_clickables"] = clickables
    return state

def ai_radio_elements(state: ApplicationState):
    body_text = state["body_text"]
    radio_elements = state["radio_elements"]

    if not radio_elements:
        return state

    prompt = f"""
You are an AI Application Helper.

Your job is to look at the body text of this page and match each radio grouping to the exact question from the page text.

body_text:
{json.dumps(body_text)}

radio_elements:
{json.dumps(radio_elements)}

Rules:
- The questions must be in the same exact order as the radio_elements list.
- Do not reorder the questions.
- Do not invent questions.
- Use the exact question text from the body_text when possible.
- If multiple radio groupings actually belong to one question, set needs_custom_grouping to True and return custom_grouping.
- custom_grouping must be a list of dictionaries.
- Each dictionary must have question, grouping, and options.
- options must contain the full radio option dictionaries that belong together.

Example:
radio_elements:
[
    {{"question": None, "grouping": "car", "options": [{{"label_text": "Honda", "index": 1}}, {{"label_text": "Toyota", "index": 4}}]}},
    {{"question": None, "grouping": "plane", "options": [{{"label_text": "Delta", "index": 8}}, {{"label_text": "American", "index": 9}}]}}
]

needs_custom_grouping: True

custom_grouping:
[
    {{
        "question": "What car do you want?",
        "grouping": "car",
        "options": [
            {{
                "tag": "input",
                "index": 1,
                "element_id": "car-honda",
                "element_type": "radio",
                "role": None,
                "aria_label": None,
                "name": "car",
                "placeholder": None,
                "value": "Honda",
                "href": None,
                "onclick": None,
                "text": "",
                "label_text": "Honda"
            }},
            {{
                "tag": "input",
                "index": 4,
                "element_id": "car-toyota",
                "element_type": "radio",
                "role": None,
                "aria_label": None,
                "name": "car",
                "placeholder": None,
                "value": "Toyota",
                "href": None,
                "onclick": None,
                "text": "",
                "label_text": "Toyota"
            }}
        ]
    }}
]

Correct response:
inside of the questions dictionary ["What car do you want?", "What plane do you like better?"]

Incorrect response:
["What plane do you like better?", "What car do you want?"]
"""

    response = multiple_question_llm.invoke(prompt)
    needs_custom_grouping = response["needs_custom_grouping"]

    if needs_custom_grouping:
        state["radio_elements"] = response["custom_grouping"]
        return state

    for i in range(min(len(radio_elements), len(response["questions"]))):
        radio_elements[i]["question"] = response["questions"][i]

    state["radio_elements"] = radio_elements

    return state

def get_all_checkboxes(state: ApplicationState):
    page = state["current_page"]["page"]
    clickables = page.locator("""[type="checkbox"], [role="checkbox"]""")

    checkbox_elements = []
    checkbox_names = []

    for i in range(clickables.count()):
        click = clickables.nth(i)

        element_data = click.evaluate("""
        el => {
            let attrs = {};
            for (const attr of el.attributes) {
                attrs[attr.name] = attr.value;
            }

            return {
                tag: el.tagName.toLowerCase(),
                element_id: attrs.id || null,
                element_type: attrs.type || null,
                role: attrs.role || null,
                aria_label: attrs["aria-label"] || null,
                name: attrs.name || null,
                placeholder: attrs.placeholder || null,
                value: attrs.value || null,
                href: attrs.href || null,
                onclick: attrs.onclick || null,
                text: el.textContent || ""
            };
        }
        """)

        name = element_data["name"]

        if name in checkbox_names:
            continue

        if name:
            checkbox_names.append(name)

        current_checkbox = []

        label_text = ""
        element_id = element_data["element_id"]
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.first.text_content() or ""

        data = {
            "tag": element_data["tag"],
            "index": i,
            "element_id": element_data["element_id"],
            "element_type": element_data["element_type"],
            "role": element_data["role"],
            "aria_label": element_data["aria_label"],
            "name": element_data["name"],
            "placeholder": element_data["placeholder"],
            "value": element_data["value"],
            "href": element_data["href"],
            "onclick": element_data["onclick"],
            "text": element_data["text"],
            "label_text": label_text
        }

        current_checkbox.append(data)

        for l in range(clickables.count()):
            if i == l:
                continue

            click2 = clickables.nth(l)

            element_data2 = click2.evaluate("""
            el => {
                let attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }

                return {
                    tag: el.tagName.toLowerCase(),
                    element_id: attrs.id || null,
                    element_type: attrs.type || null,
                    role: attrs.role || null,
                    aria_label: attrs["aria-label"] || null,
                    name: attrs.name || null,
                    placeholder: attrs.placeholder || null,
                    value: attrs.value || null,
                    href: attrs.href || null,
                    onclick: attrs.onclick || null,
                    text: el.textContent || ""
                };
            }
            """)

            name2 = element_data2["name"]

            if name != name2:
                continue

            label_text2 = ""
            element_id2 = element_data2["element_id"]
            if element_id2:
                label2 = page.locator(f'[for="{element_id2}"]')
                if label2.count() > 0:
                    label_text2 = label2.first.text_content() or ""

            data2 = {
                "tag": element_data2["tag"],
                "index": l,
                "element_id": element_data2["element_id"],
                "element_type": element_data2["element_type"],
                "role": element_data2["role"],
                "aria_label": element_data2["aria_label"],
                "name": element_data2["name"],
                "placeholder": element_data2["placeholder"],
                "value": element_data2["value"],
                "href": element_data2["href"],
                "onclick": element_data2["onclick"],
                "text": element_data2["text"],
                "label_text": label_text2
            }

            current_checkbox.append(data2)

        checkbox_elements.append({
            "grouping": name,
            "question": None,
            "options": current_checkbox
        })

    state["checkbox_elements"] = checkbox_elements
    state["checkbox_elements_clickables"] = clickables
    return state

def ai_checkbox_elements(state: ApplicationState):
    body_text = state["body_text"]
    checkbox_elements = state["checkbox_elements"]

    if not checkbox_elements:
        return state

    prompt = f"""
You are an AI Application Helper.

Your job is to look at the body text of this page and match each checkbox grouping to the exact question from the page text.

body_text:
{json.dumps(body_text)}

checkbox_elements:
{json.dumps(checkbox_elements)}

Rules:
- The questions must be in the same exact order as the checkbox_elements list.
- Do not reorder the questions.
- Do not invent questions.
- Use the exact question text from the body_text when possible.
- If multiple checkbox groupings actually belong to one question, set needs_custom_grouping to True and return custom_grouping.
- custom_grouping must be a list of dictionaries.
- Each dictionary must have question, grouping, and options.
- options must contain the full checkbox option dictionaries that belong together.

Example:
checkbox_elements:
[
    {{"question": None, "grouping": "skills", "options": [{{"label_text": "Python", "index": 1}}, {{"label_text": "Java", "index": 4}}]}},
    {{"question": None, "grouping": "ethnicity", "options": [{{"label_text": "Hispanic or Latino", "index": 8}}, {{"label_text": "Asian", "index": 9}}]}}
]

needs_custom_grouping: True

custom_grouping:
[
    {{
        "question": "Which skills do you have?",
        "grouping": "skills",
        "options": [
            {{
                "tag": "input",
                "index": 1,
                "element_id": "skill-python",
                "element_type": "checkbox",
                "role": None,
                "aria_label": None,
                "name": "skills",
                "placeholder": None,
                "value": "Python",
                "href": None,
                "onclick": None,
                "text": "",
                "label_text": "Python"
            }},
            {{
                "tag": "input",
                "index": 4,
                "element_id": "skill-java",
                "element_type": "checkbox",
                "role": None,
                "aria_label": None,
                "name": "skills",
                "placeholder": None,
                "value": "Java",
                "href": None,
                "onclick": None,
                "text": "",
                "label_text": "Java"
            }}
        ]
    }}
]

Correct response:
inside of the questions dictionary ["Which skills do you have?", "What is your ethnicity?"]

Incorrect response:
["What is your ethnicity?", "Which skills do you have?"]
"""

    response = multiple_question_llm.invoke(prompt)
    needs_custom_grouping = response["needs_custom_grouping"]

    if needs_custom_grouping:
        state["checkbox_elements"] = response["custom_grouping"]
        return state

    for i in range(min(len(checkbox_elements), len(response["questions"]))):
        checkbox_elements[i]["question"] = response["questions"][i]

    state["checkbox_elements"] = checkbox_elements

    return state

def signup_process(state: ApplicationState):
    page = state["current_page"]["page"]

    get_all_elements(state)
    get_all_radio(state)
    get_all_checkboxes(state)
    get_all_select(state)
    get_all_datalist(state)

    body_text = page.locator("body").inner_text()
    all_elements = state["all_elements"]
    radio_elements = state["radio_elements"]
    checkbox_elements = state["checkbox_elements"]
    select_elements = state["select_elements"]
    datalist_elements = state["datalist_elements"]
    prompt = f"""
Your an AI Applicant helper and your job is to look through the elements and body text to return the indexes that we are going to use
to be able to create an account or signup. Then you are also going to look for the follow through button and return it's index to be able to submit or
go to the next page.

Ex:
 {{"input_indexes": [12, 15, 30]}}, {{"input_indexes_reason": The elements contain the input attributes.}} {{"follow_through_element": 49}}, {{"follow_through_reason": It the element name Create account with it's attribute's saying submit.}}

 all_elements: {json.dumps(all_elements)}
 radio_elements: {json.dumps(radio_elements)}
 checkbox_elements: {json.dumps(checkbox_elements)}
 select_elements: {json.dumps(select_elements)}
 datalist_elements: {json.dumps(datalist_elements)}

 body_text: {json.dumps(body_text)}
"""
    response = signup_process_llm.invoke(prompt)
    state["signup_process"] = {
        "input_indexes": response["input_indexes"],
        "input_indexes_reason": response["input_indexes_reason"],
        "radio_indexes": response["radio_indexes"],
        "radio_indexes_reason": response["radio_indexes_reason"],
        "checkbox_indexes": response["checkbox_indexes"],
        "checkbox_indexes_reason": response["checkbox_indexes_reason"],
        "select_indexes": response["select_indexes"],
        "select_indexes_reason": response["select_indexes_reason"],
        "datalist_indexes": response["datalist_indexes"],
        "datalist_indexes_reason": response["datalist_indexes_reason"],
        "follow_through_element": response["follow_through_element"],
        "follow_through_reason": response["follow_through_reason"]
    }
    print(state["signup_process"])
    return state
    

def cookies_process(state: ApplicationState):
    page = state["current_page"]["page"]

    get_all_elements(state)

    body_text = page.locator("body").inner_text()
    all_elements = state["all_elements"]

    prompt = f"""
Your job is to determine the element that we need to click to accept cookies by its index and the reason why we are clicking that element.

We also need to determine which process we are going to next.

Actions:
- signup: We need to sign up or login.
- forms: We need to fill out forms.
- other: Not an error, but a custom action is needed.
- error: The page is not working and we need to leave.

Return this exact structure:
{{
  "follow_through_index": 4,
  "follow_through_reason": "The text says accept cookies.",
  "action": "forms",
  "action_reason": "The page has form fields that need to be filled out."
}}
 
body_text:
{body_text}

all_elements:
{all_elements}
"""

    response = cookies_process_llm.invoke(prompt)

    state["cookies_response"] = response
    print(state["cookies_response"])

    cookies_action(state)

    return state


def cookies_action(state: ApplicationState):
    page = state["current_page"]["page"]

    clickables = state["all_elements_clickables"]

    cookies_process = state["cookies_response"]

    follow_through_index = cookies_process["follow_through_index"]
    action = cookies_process["action"]

    if follow_through_index is None:
        return action

    click = clickables.nth(follow_through_index)

    try:
        with page.expect_popup(timeout=5000) as popup_info:
            click.click()

        new_page = popup_info.value
        new_page.wait_for_load_state("networkidle", timeout=5000)

        state["current_page"]["page"] = new_page
        state["current_page"]["url"] = new_page.url

    except TimeoutError:
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except TimeoutError:
            state["previous_action"] = "error"
            return state

        state["current_page"]["url"] = page.url

    return state

def get_all_select(state: ApplicationState):
    page = state["current_page"]["page"]
    clickables = page.locator("select")

    select_elements = []

    for i in range(clickables.count()):
        click = clickables.nth(i)

        element_data = click.evaluate("""
        el => {
            let attrs = {};
            for (const attr of el.attributes) {
                attrs[attr.name] = attr.value;
            }

            let options = [];
            for (let i = 0; i < el.options.length; i++) {
                let option = el.options[i];

                options.push({
                    tag: option.tagName.toLowerCase(),
                    index: i,
                    value: option.value || null,
                    text: option.textContent || ""
                });
            }

            return {
                tag: el.tagName.toLowerCase(),
                element_id: attrs.id || null,
                element_type: attrs.type || null,
                role: attrs.role || null,
                aria_label: attrs["aria-label"] || null,
                name: attrs.name || null,
                placeholder: attrs.placeholder || null,
                value: el.value || attrs.value || null,
                href: attrs.href || null,
                onclick: attrs.onclick || null,
                text: el.textContent || "",
                options: options
            };
        }
        """)

        label_text = ""
        element_id = element_data["element_id"]
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.first.text_content() or ""

        data = {
            "tag": element_data["tag"],
            "index": i,
            "element_id": element_data["element_id"],
            "element_type": element_data["element_type"],
            "role": element_data["role"],
            "aria_label": element_data["aria_label"],
            "name": element_data["name"],
            "placeholder": element_data["placeholder"],
            "value": element_data["value"],
            "href": element_data["href"],
            "onclick": element_data["onclick"],
            "text": element_data["text"],
            "label_text": label_text,
            "options": element_data["options"]
        }

        select_elements.append({
            "grouping": element_data["name"],
            "question": None,
            "options": [data]
        })

    state["select_elements"] = select_elements
    state["select_elements_clickables"] = clickables
    return state

def ai_select_elements(state: ApplicationState):
    body_text = state["body_text"]
    select_elements = state["select_elements"]

    if not select_elements:
        return state

    prompt = f"""
You are an AI Application Helper.

Your job is to look at the body text of this page and match each select/dropdown grouping to the exact question from the page text.

body_text:
{json.dumps(body_text)}

select_elements:
{json.dumps(select_elements)}

Rules:
- The questions must be in the same exact order as the select_elements list.
- Do not reorder the questions.
- Do not invent questions.
- Use the exact question text from the body_text when possible.
- Each select element usually belongs to one question.
- If multiple select groupings actually belong to one question, set needs_custom_grouping to True and return custom_grouping.
- custom_grouping must be a list of dictionaries.
- Each dictionary must have question, grouping, and options.
- options must contain the full select option dictionaries that belong together.

Example:
select_elements:
[
    {{"question": None, "grouping": "country", "options": [{{"label_text": "Country", "index": 1}}]}},
    {{"question": None, "grouping": "state", "options": [{{"label_text": "State", "index": 2}}]}}
]

Correct response:
inside of the questions dictionary ["What country do you live in?", "What state do you live in?"]

Incorrect response:
["What state do you live in?", "What country do you live in?"]
"""

    response = multiple_question_llm.invoke(prompt)
    needs_custom_grouping = response["needs_custom_grouping"]

    if needs_custom_grouping:
        state["select_elements"] = response["custom_grouping"]
        return state

    for i in range(min(len(select_elements), len(response["questions"]))):
        select_elements[i]["question"] = response["questions"][i]

    state["select_elements"] = select_elements

    return state

def get_all_datalist(state: ApplicationState):
    page = state["current_page"]["page"]
    clickables = page.locator("input[list]")

    datalist_elements = []

    for i in range(clickables.count()):
        click = clickables.nth(i)

        element_data = click.evaluate("""
        el => {
            let attrs = {};
            for (const attr of el.attributes) {
                attrs[attr.name] = attr.value;
            }

            let current_options = [];
            let list_id = attrs.list || null;

            if (list_id) {
                let datalist = document.querySelector(`datalist[id="${list_id}"]`);

                if (datalist) {
                    let options = datalist.querySelectorAll("option");

                    for (let i = 0; i < options.length; i++) {
                        let option = options[i];

                        current_options.push({
                            tag: option.tagName.toLowerCase(),
                            index: i,
                            value: option.value || null,
                            text: option.textContent || ""
                        });
                    }
                }
            }

            return {
                tag: el.tagName.toLowerCase(),
                element_id: attrs.id || null,
                element_type: attrs.type || null,
                role: attrs.role || null,
                aria_label: attrs["aria-label"] || null,
                name: attrs.name || null,
                placeholder: attrs.placeholder || null,
                value: attrs.value || el.value || null,
                href: attrs.href || null,
                onclick: attrs.onclick || null,
                text: el.textContent || "",
                list_id: list_id,
                options: current_options
            };
        }
        """)

        label_text = ""
        element_id = element_data["element_id"]
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.first.text_content() or ""

        data = {
            "tag": element_data["tag"],
            "index": i,
            "element_id": element_data["element_id"],
            "element_type": element_data["element_type"],
            "role": element_data["role"],
            "aria_label": element_data["aria_label"],
            "name": element_data["name"],
            "placeholder": element_data["placeholder"],
            "value": element_data["value"],
            "href": element_data["href"],
            "onclick": element_data["onclick"],
            "text": element_data["text"],
            "label_text": label_text,
            "options": element_data["options"]
        }

        datalist_elements.append({
            "grouping": element_data["name"],
            "question": None,
            "options": [data]
        })

    state["datalist_elements"] = datalist_elements
    state["datalist_elements_clickables"] = clickables
    return state

def ai_datalist_elements(state: ApplicationState):
    body_text = state["body_text"]
    datalist_elements = state["datalist_elements"]

    if not datalist_elements:
        return state

    prompt = f"""
You are an AI Application Helper.

Your job is to look at the body text of this page and match each datalist grouping to the exact question from the page text.

body_text:
{json.dumps(body_text)}

datalist_elements:
{json.dumps(datalist_elements)}

Rules:
- The questions must be in the same exact order as the datalist_elements list.
- Do not reorder the questions.
- Do not invent questions.
- Use the exact question text from the body_text when possible.
- Each datalist element usually belongs to one question.
- If multiple datalist groupings actually belong to one question, set needs_custom_grouping to True and return custom_grouping.
- custom_grouping must be a list of dictionaries.
- Each dictionary must have question, grouping, and options.
- options must contain the full datalist option dictionaries that belong together.

Example:
datalist_elements:
[
    {{"question": None, "grouping": "country", "options": [{{"label_text": "Country", "index": 1}}]}},
    {{"question": None, "grouping": "state", "options": [{{"label_text": "State", "index": 2}}]}}
]

Correct response:
inside of the questions dictionary ["What country do you live in?", "What state do you live in?"]

Incorrect response:
["What state do you live in?", "What country do you live in?"]
"""

    response = multiple_question_llm.invoke(prompt)
    needs_custom_grouping = response["needs_custom_grouping"]

    if needs_custom_grouping:
        state["datalist_elements"] = response["custom_grouping"]
        return state

    for i in range(min(len(datalist_elements), len(response["questions"]))):
        datalist_elements[i]["question"] = response["questions"][i]

    state["datalist_elements"] = datalist_elements

    return state

def hidden_elements(state: ApplicationState):
    page = state["current_page"]["page"]
    elements = """
[display="none"], [visibility="hidden"], [content-visibility="hidden"], hidden
"""
    clickables = page.locator(elements)

def answer_all_elements(state: ApplicationState):
    page = state["current_page"]["page"]
    body_text = state["body_text"]
    all_elements = state["all_elements"]
    clickables = state["all_elements_clickables"]
    for i in range(min(len(all_elements), clickables.count())):
        current_element = all_elements[i]
        state["current_element"] = current_element
        click = clickables.nth(i)
        state["click"] = click
        prompt = f"""
Your an AI Applicant helper your job is to look at the current element and the body text and decide the best next action
- what each action does
    - fill_text: this is the option if you want to just fill in the element with text.
    - choose options: you have looked at all the question and all it's options and have determine which option(s) you would like to choose.
    - check box: you have looked at the question and it's checkboxes and have determine that we should check certain boxes (only use when there are checkboxes present).
    - click button: this is useful when you just want to click a button.
    - click & expand: this is useful when you have things like add work experience so you can see all the new elements after clicking.
    - click & screenshot: this is useful when you are a bit lost and confused and you think clicking and screenshot is the best line of action to help understanding the question and it's options.
    - upload resume: this is useful when you need to upload the user's resume.
    - upload cover letter: this is useful when you need to upload the user's cover letter.
    - screenshot: this is useful when you don't need to click anything but need to screenshot to understand what's going on.
    - need more content: this is useful when you just need to look at the sister and/or parent and/or child elements and nothing else, you can also call those any time you want.
    - skip: this is useful if you believe that the element isn't useful, question shouldn't be answered because it is not required, or that it is not useful to the user's profile.
Also when you believe that you have completed the line of action with the element whether you are skipping or you have completed the element that is when you mark the element_continue as True.

current_element: {json.dumps(current_element)}
body_text: {json.dumps(body_text)}
"""
    response = forms_action_llm.invoke(prompt)
    state["element_action"] = {
        "action": response["action"],
        "answer": response["answer"],
        "option_answer_index": response["option_answer_index"],
        "needs_options": response["needs_options"],
        "needs_children_elements": response["needs_children_elements"],
        "needs_sister_elements": response["needs_sister_elements"],
        "needs_parent_elements": response["needs_parent_elements"],
        "element_done": response["element_done"],
        "reason": response["reason"]
    }

def process_question(state: ApplicationState):
    page = state["current_page"]["page"]
    current_element = state["current_element"]
    current_click = state["current_click"]
    current_child_elements = state["current_child_elements"] or ""
    current_sister_elements = state["current_sister_elements"] or ""
    current_parent_elements = state["current_parent_elements"] or ""
    body_text = state["body_text"]
    tracker = 0
    for i in range(4):
        prompt = f"""
Your an AI Applicant helper your job is to look at the current element and the body text and decide the best next action
- what each action does
    - fill_text: this is the option if you want to just fill in the element with text.
    - choose options: you have looked at all the question and all it's options and have determine which option(s) you would like to choose.
    - check box: you have looked at the question and it's checkboxes and have determine that we should check certain boxes (only use when there are checkboxes present).
    - click button: this is useful when you just want to click a button.
    - click & expand: this is useful when you have things like add work experience so you can see all the new elements after clicking.
    - click & screenshot: this is useful when you are a bit lost and confused and you think clicking and screenshot is the best line of action to help understanding the question and it's options.
    - upload resume: this is useful when you need to upload the user's resume.
    - upload cover letter: this is useful when you need to upload the user's cover letter.
    - screenshot: this is useful when you don't need to click anything but need to screenshot to understand what's going on.
    - need more content: this is useful when you just need to look at the sister and/or parent and/or child elements and nothing else, you can also call those any time you want.
    - continue: this is useful if you believe that the element isn't useful, question shouldn't be answered because it is not required, or that it is not useful to the user's profile.
Also when you believe that you have completed the line of action with the element whether you are skipping or you have completed the element that is when you mark the element_continue as True.

current_element: {json.dumps(current_element)}
current_child_elements: {json.dumps(current_child_elements)}
current_sister_elements: {json.dumps}
body_text: {json.dumps(body_text)}
"""
        response = forms_action_llm.invoke(prompt)
        tracker += 1
        action = response["action"]
        answer_text = response["action"]
        option_answer_index = response["option_answer_index"]
        needs_options = response["needs_options"]
        needs_child_elements = response["needs_child_elements"]
        needs_sister_elements = response["needs_sister_elements"]
        needs_parent_elements = response["needs_parent_element"]
        element_done = response["element_done"]

        if action == "fill_text":
            current_click.fill(answer_text)
        if action == "click":
            current_click.click()
        if action == "click_and_expand":
            current_click.click()
            if needs_child_elements:
                get_child_elements(state)
            if needs_sister_elements:
                print("hello")
            if needs_parent_elements:
                print("hell0")
        

def get_child_elements(state):
    page = state["current_page"]
    current_click = state["current_click"]
    child_elements = current_click.locator("> *")
    all_child_elements = []
    for i in range(child_elements.count()):
        element = child_elements.nth(i)
        tag = element.evaluate("el => el.tagName.toLowerCase")
        index = i
        element_id = element.get_attribute("id") or ""
        label_text = ""
        if element_id:
            label = page.locator([f'[for="{element_id}"]'])
            if label:
                label_text = label.text_content()
        attributes = element.evaluate("""
el => {
    let elementAttribute = [];
    for (const attr of el.attributes) {
        elementAttribute.push({ name: attr.name, value: attr.value });
    }
    return elementAttribute;
}                                   
""")
        all_child_elements.append({
            "tag": tag,
            "index": index,
            "element_id": element_id,
            "label_text": label_text,
            "attributes": attributes
        })
        state["current_child_element"] = all_child_elements
        return state

def load_test_user(state: ApplicationState):
    state["user_id"] = "12345"

    state["first_name"] = "John"
    state["last_name"] = "Doe"
    state["preferred_name"] = "John"

    state["email"] = "john.doe@email.com"
    state["password"] = "Passwor123!"
    state["phone_number"] = "9195551234"

    state["address_line1"] = "123 Main Street"
    state["address_line2"] = ""
    state["city"] = "Charlotte"
    state["user_state"] = "NC"
    state["zip_code"] = "28223"
    state["country"] = "United States"

    state["work_authorized"] = True
    state["requires_sponsorship"] = False
    state["veteran"] = False
    state["disability"] = False

    state["linkedin_url"] = "https://linkedin.com/in/johndoe"
    state["github_url"] = "https://github.com/johndoe"
    state["portfolio_url"] = "https://johndoe.dev"

    state["resume_text"] = """
John Doe
Software Engineering Student

Education
UNC Charlotte
B.S. Computer Science

Skills
Python
Java
SQL
JavaScript
FastAPI
Playwright

Experience
Software Engineering Intern
Developed automation tools using Python and Playwright.
"""

    state["resume_upload"] = "resume.pdf"

    state["cover_letter_text"] = """
Dear Hiring Manager,

I am excited to apply for this position because I enjoy building automation software and AI systems.

Thank you for your consideration.
"""

    state["cover_letter_upload"] = "cover_letter.pdf"

    return state

import json
import time
from typing import TypedDict, Literal
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# IMPORTANT:
# Use include_raw=True so we can track tokens.
page_decision_llm = llm.with_structured_output(PageDecision, include_raw=True)


# =========================
# TOKEN TRACKING
# =========================

def setup_token_usage(state):
    if "token_usage" not in state:
        state["token_usage"] = {
            "calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }

    return state


def invoke_and_track(llm, prompt, state):
    setup_token_usage(state)

    response = llm.invoke(prompt)

    raw = response.get("raw")
    parsed = response.get("parsed")

    usage = {}

    if raw and hasattr(raw, "usage_metadata") and raw.usage_metadata:
        usage = raw.usage_metadata

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

    state["token_usage"]["calls"] += 1
    state["token_usage"]["input_tokens"] += input_tokens
    state["token_usage"]["output_tokens"] += output_tokens
    state["token_usage"]["total_tokens"] += total_tokens

    INPUT_PRICE = 0.05 / 1_000_000
    OUTPUT_PRICE = 0.40 / 1_000_000

    input_cost = state["token_usage"]["input_tokens"] * INPUT_PRICE
    output_cost = state["token_usage"]["output_tokens"] * OUTPUT_PRICE
    total_cost = input_cost + output_cost

    state["token_usage"]["estimated_cost"] = total_cost

    print("\n" + "=" * 70)
    print(f"LLM CALL #{state['token_usage']['calls']}")
    print("-" * 70)
    print("THIS CALL")
    print(f"Input Tokens : {input_tokens:,}")
    print(f"Output Tokens: {output_tokens:,}")
    print(f"Total Tokens : {total_tokens:,}")
    print("-" * 70)
    print("RUNNING TOTAL")
    print(f"Input Tokens : {state['token_usage']['input_tokens']:,}")
    print(f"Output Tokens: {state['token_usage']['output_tokens']:,}")
    print(f"Total Tokens : {state['token_usage']['total_tokens']:,}")
    print(f"Estimated Cost: ${total_cost:.5f}")
    print("=" * 70 + "\n")

    return parsed


def print_final_token_summary(state):
    usage = state.get("token_usage", {})

    print("\n" + "=" * 70)
    print("FINAL APPLICATION TOKEN SUMMARY")
    print("-" * 70)
    print(f"LLM Calls     : {usage.get('calls', 0):,}")
    print(f"Input Tokens  : {usage.get('input_tokens', 0):,}")
    print(f"Output Tokens : {usage.get('output_tokens', 0):,}")
    print(f"Total Tokens  : {usage.get('total_tokens', 0):,}")
    print(f"Estimated Cost: ${usage.get('estimated_cost', 0):.5f}")
    print("=" * 70 + "\n")


# =========================
# GET ALL ELEMENTS
# =========================

def get_all_elements(state):
    page = state["current_page"]["page"]

    selector = """
a[href],
button,
input,
textarea,
select,
option,
[contenteditable="true"],
[role="button"],
[role="link"],
[role="radio"],
[role="checkbox"],
[role="combobox"],
[role="listbox"],
[role="option"],
[role="switch"],
[role="tab"],
[role="menuitem"],
[role="menuitemcheckbox"],
[role="menuitemradio"]
"""

    clickables = page.locator(selector)
    all_elements = []

    for i in range(clickables.count()):
        element = clickables.nth(i)

        try:
            tag = element.evaluate("el => el.tagName.toLowerCase()")
        except:
            tag = ""

        element_id = element.get_attribute("id") or ""
        element_type = element.get_attribute("type") or ""
        role = element.get_attribute("role") or ""
        aria_label = element.get_attribute("aria-label") or ""
        name = element.get_attribute("name") or ""
        placeholder = element.get_attribute("placeholder") or ""
        value = element.get_attribute("value") or ""
        href = element.get_attribute("href") or ""
        onclick = element.get_attribute("onclick") or ""

        try:
            text = element.text_content() or ""
        except:
            text = ""

        label_text = ""
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.text_content() or ""

        try:
            attributes = element.evaluate("""
el => [...el.attributes].map(attr => ({
    name: attr.name,
    value: attr.value
}))
""")
        except:
            attributes = []

        all_elements.append({
            "index": i,
            "tag": tag,
            "element_id": element_id,
            "element_type": element_type,
            "role": role,
            "aria_label": aria_label,
            "name": name,
            "placeholder": placeholder,
            "value": value,
            "href": href,
            "onclick": onclick,
            "text": text.strip(),
            "label_text": label_text.strip(),
            "attributes": attributes
        })

    state["all_elements"] = all_elements
    state["all_elements_clickables"] = clickables
    state["body_text"] = page.locator("body").inner_text() or ""

    return state


# =========================
# AI PAGE DECISION
# =========================

def ai_page_decision(state):
    body_text = state["body_text"]
    all_elements = state["all_elements"]
    user_profile = {
        "user_id": state.get("user_id"),
        "first_name": state.get("first_name"),
        "last_name": state.get("last_name"),
        "preferred_name": state.get("preferred_name"),
        "email": state.get("email"),
        "phone_number": state.get("phone_number"),

        "address_line1": state.get("address_line1"),
        "address_line2": state.get("address_line2"),
        "city": state.get("city"),
        "user_state": state.get("user_state"),
        "zip_code": state.get("zip_code"),
        "country": state.get("country"),

        "work_authorized": state.get("work_authorized"),
        "requires_sponsorship": state.get("requires_sponsorship"),
        "veteran": state.get("veteran"),
        "disability": state.get("disability"),

        "linkedin_url": state.get("linkedin_url"),
        "github_url": state.get("github_url"),
        "portfolio_url": state.get("portfolio_url"),

        "resume_text": state.get("resume_text"),
        "resume_upload": state.get("resume_upload"),
        "cover_letter_text": state.get("cover_letter_text"),
        "cover_letter_upload": state.get("cover_letter_upload"),

        "url": state.get("url"),
        "company_name": state.get("company_name"),
        "company_position": state.get("company_position"),
    }

    prompt = f"""
You are an AI Applicant Helper.

You are given the entire page text and every interactive element on the page.

Your job is to decide every useful action needed on this page.

You can:
- fill text inputs
- click buttons
- click radio buttons
- check checkboxes
- select dropdown options
- upload resume
- upload cover letter
- skip useless elements
- decide if the page should continue, finish, ask for more context, or error
- decide the continue/save/next/submit button

Rules:
- Look at the entire page before deciding.
- Use the element indexes from all_elements.
- Do not click destructive actions.
- Do not click random links.
- Do not submit the final application unless the page clearly says submit and all required fields are complete.
- Only answer questions that are required or useful.
- If a field is already filled, skip it.
- For dropdowns, use select_option.
- For checkboxes, use check_box.
- For radio buttons or normal buttons, use click.
- For file inputs, use upload_resume or upload_cover_letter.
- If the page needs to move forward, set page_status to "continue" and set follow_through_element.
- If the application/forms are fully done, set page_status to "finished".
- If the page is confusing and needs screenshot/html refresh, set page_status to "need_more_context".
- If the page is broken or impossible, set page_status to "error".

Return this exact structure:
{{
    "actions_to_take": [
        {{
            "action": "fill_text",
            "element_index": 4,
            "answer": "John",
            "reason": "This field asks for first name."
        }}
    ],
    "page_status": "continue",
    "follow_through_element": 22,
    "reason": "All required fields are complete and the continue button should be clicked."
}}

user_profile:
{json.dumps(user_profile, indent=2)}

body_text:
{json.dumps(body_text)}

all_elements:
{json.dumps(all_elements, indent=2)}
"""

    decision = invoke_and_track(page_decision_llm, prompt, state)
    state["page_decision"] = decision

    print("\nAI PAGE DECISION:")
    print(json.dumps(decision, indent=2))

    return state


# =========================
# EXECUTE AI ACTIONS
# =========================

def execute_page_decision(state):
    page = state["current_page"]["page"]
    clickables = state["all_elements_clickables"]
    decision = state["page_decision"]

    actions = decision["actions_to_take"]

    for action_item in actions:
        action = action_item["action"]
        index = action_item["element_index"]
        answer = action_item["answer"]

        if index is None:
            continue

        element = clickables.nth(index)

        print(f"\nExecuting: {action} on index {index}")
        print(f"Reason: {action_item['reason']}")

        try:
            if action == "fill_text":
                if answer:
                    element.fill(answer)

            elif action == "click":
                element.click()

            elif action == "check_box":
                try:
                    element.check()
                except:
                    element.click()

            elif action == "select_option":
                if answer:
                    try:
                        element.select_option(label=answer)
                    except:
                        try:
                            element.select_option(value=answer)
                        except:
                            element.click()

            elif action == "upload_resume":
                resume_path = state["user_profile"]["resume_path"]
                element.set_input_files(resume_path)

            elif action == "upload_cover_letter":
                cover_letter_path = state["user_profile"]["cover_letter_path"]
                element.set_input_files(cover_letter_path)

            elif action == "skip":
                continue

            time.sleep(0.3)

        except Exception as e:
            print(f"Failed action {action} on index {index}: {e}")

    return state


# =========================
# CONTINUE / FINISH PAGE
# =========================

def continue_or_finish_page(state):
    page = state["current_page"]["page"]
    clickables = state["all_elements_clickables"]
    decision = state["page_decision"]

    page_status = decision["page_status"]
    follow_through_element = decision["follow_through_element"]

    if page_status == "finished":
        state["forms_done"] = True
        print("Forms finished.")
        return state

    if page_status == "error":
        state["forms_error"] = True
        print("Forms error.")
        return state

    if page_status == "need_more_context":
        state["needs_more_context"] = True
        print("Needs more context.")
        return state

    if page_status == "continue" and follow_through_element is not None:
        button = clickables.nth(follow_through_element)

        print(f"\nClicking follow-through element: {follow_through_element}")

        try:
            with page.expect_popup(timeout=5000) as popup_info:
                button.click()

            new_page = popup_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=15000)

            state["current_page"]["page"] = new_page
            state["current_page"]["url"] = new_page.url

            print(f"Moved to new popup page: {new_page.url}")

        except PlaywrightTimeoutError:
            try:
                button.click()
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except:
                pass

            state["current_page"]["url"] = page.url
            print(f"Stayed on same page: {page.url}")

    return state


# =========================
# ONE PAGE FORM PROCESS
# =========================

def complete_current_form_page(state):
    get_all_elements(state)
    ai_page_decision(state)
    execute_page_decision(state)
    continue_or_finish_page(state)

    return state


# =========================
# FULL APPLICATION FORM LOOP
# =========================

def complete_application_forms(state):
    setup_token_usage(state)

    state["forms_done"] = False
    state["forms_error"] = False
    state["needs_more_context"] = False

    for page_attempt in range(20):
        print("\n" + "#" * 70)
        print(f"FORM PAGE ATTEMPT #{page_attempt + 1}")
        print("#" * 70)

        complete_current_form_page(state)

        if state.get("forms_done"):
            break

        if state.get("forms_error"):
            break

        if state.get("needs_more_context"):
            break

        time.sleep(1)

    print_final_token_summary(state)

    return state

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


def opening_page(state: ApplicationState):
    url = state["url"]
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = browser.new_page()
    page.goto(url)
    url = page.url
    state["current_page"] = {
        "page": page,
        "url": url,
        "browser": browser,
        "context": context
    }
    return state



from langgraph.graph import StateGraph, START, END

graph = StateGraph(ApplicationState)

graph.add_node("opening_page", opening_page)
graph.add_node("load_user", load_test_user)
graph.add_node("decide_page", decide_page)
graph.add_node("apply_process", apply_process)
graph.add_node("cookies_process", cookies_process)
graph.add_node("signup_process", signup_process)
graph.add_node("complete_applications", complete_application_forms)

graph.add_edge(START, "load_user")
graph.add_edge("load_user", "opening_page")
graph.add_edge("opening_page", "decide_page")
graph.add_conditional_edges("decide_page", decide_routing, {
    "apply": "apply_process",
    "cookies": "cookies_process",
    "signup": "complete_applications",
    "error": END
})
graph.add_edge("apply_process", "decide_page")
graph.add_edge("cookies_process", "decide_page")
graph.add_edge("signup_process", END)

mapping = graph.compile()

with Stealth().use_sync(sync_playwright()) as p:
    mapping.invoke({"url": url})
