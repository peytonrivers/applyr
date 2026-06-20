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
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess

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
        state1 = process_cookies(state)
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

def decide_page(state: ApplicationState):
    action = state.get("decide_page", {}).get("action", None)

    if action == "error":
        print("An error has occurred in one of the previous pages")
        browser = state["current_page"]["browser"]
        browser.close()
        return "error"

    page = state["current_page"]["page"]
    body_text = page.locator("body").inner_text() or ""

    get_all_elements(state)
    all_elements = state["all_elements"]

    screenshot_base64 = get_page_screenshot_base64(page)

    prompt = f"""
Your job is to look at the body text, all the elements, and the screenshot to determine what type of page this is, make sure 
you use common sense when choosing which type of page it is as well.

- apply: You choose this page if this is the opening page where we need to click apply now or start the application process.
- signup: You choose this page strictly if we are required to sign up or login before continuing.
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

    return state

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
        current_element = []
        click = clickables.nth(i)
        element_type = click.get_attribute("type")
        if element_type == "checkbox" or element_type == "radio":
            continue
        tag = click.evaluate("el => el.tagName.toLowerCase()")
        index = i
        element_id = click.get_attribute("id")
        role = click.get_attribute("role")
        aria_label = click.get_attribute("aria-label")
        name = click.get_attribute("name")
        placeholder = click.get_attribute("placeholder")
        value = click.get_attribute("value")
        text = click.text_content() or ""
        href = click.get_attribute("href")
        onclick = click.get_attribute("onclick")
        label_text = ""
        if element_id:
            label = page.locator(f'[for="{element_id}"]') or None
            if label.count() > 0:
                label_text = label.first.text_content() or ""
        data = {
            "tag": tag,
            "index": i,
            "element_id": element_id,
            "element_type": element_type,
            "role": role,
            "aria_label": aria_label,
            "name": name,
            "placeholder": placeholder,
            "value": value,
            "href": href,
            "onclick": onclick,
            "text": text,
            "label_text": label_text
        }
        current_element.append(data)
        all_elements.append({"question": None, "option": current_element})
    state["body_text"] = page.locator("body").inner_text()
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
        name = click.get_attribute("name")
        if name in radio_names:
            continue
        if name:
            radio_names.append(name)
        current_radio = []
        tag = click.evaluate("el => el.tagName.toLowerCase()")
        index = i
        element_id = click.get_attribute("id")
        element_type = click.get_attribute("type")
        role = click.get_attribute("role")
        aria_label = click.get_attribute("aria-label")
        name = click.get_attribute("name")
        placeholder = click.get_attribute("placeholder")
        value = click.get_attribute("value")
        text = click.text_content() or ""
        href = click.get_attribute("href")
        onclick = click.get_attribute("onclick")
        label_text = ""
        if element_id:
            label = page.locator(f'[for="{element_id}"]') or None
            if label.count() > 0:
                label_text = label.first.text_content() or ""
        data = {
            "tag": tag,
            "index": i,
            "element_id": element_id,
            "element_type": element_type,
            "role": role,
            "aria_label": aria_label,
            "name": name,
            "placeholder": placeholder,
            "value": value,
            "href": href,
            "onclick": onclick,
            "text": text,
            "label_text": label_text
        }
        current_radio.append(data)
        for l in range(clickables.count()):
            if i == l:
                continue
            click2 = clickables.nth(l)
            name2 = click2.get_attribute("name")
            if name != name2:
                continue
            tag2 = click2.evaluate("el => el.tagName.toLowerCase()")
            element_id2 = click2.get_attribute("id")
            element_type2 = click2.get_attribute("type")
            role2 = click2.get_attribute("role")
            aria_label2 = click2.get_attribute("aria-label")
            name2 = click2.get_attribute("name")
            placeholder2 = click2.get_attribute("placeholder")
            value2 = click2.get_attribute("value")
            href2 = click2.get_attribute("href")
            onclick2 = click2.get_attribute("onclick")
            text2 = click2.text_content() or ""
            label_text2 = ""
            if element_id2:
                label2 = page.locator(f'[for="{element_id2}"]')
                if label2.count() > 0:
                    label_text2 = label2.text_content() or ""
            data2 = {
                "tag": tag2,
                "index": l,
                "element_id": element_id2,
                "element_type": element_type2,
                "role": role2,
                "aria_label": aria_label2,
                "name": name2,
                "placeholder": placeholder2,
                "value": value2,
                "href": href2,
                "onclick": onclick2,
                "text": text2,
                "label_text": label_text2
            }
            current_radio.append(data2)
        radio_elements.append({"grouping": name, "question": None, "options": current_radio})


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
        name = click.get_attribute("name")

        if name in checkbox_names:
            continue

        checkbox_names.append(name)
        current_checkbox = []

        tag = click.evaluate("el => el.tagName.toLowerCase()")
        element_id = click.get_attribute("id")
        input_type = click.get_attribute("type")
        role = click.get_attribute("role")
        aria_label = click.get_attribute("aria-label")
        name = click.get_attribute("name")
        placeholder = click.get_attribute("placeholder")
        value = click.get_attribute("value")
        text = click.text_content() or ""
        href = click.get_attribute("href")
        onclick = click.get_attribute("onclick")

        label_text = ""
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.first.text_content() or ""

        data = {
            "tag": tag,
            "index": i,
            "element_id": element_id,
            "element_type": input_type,
            "role": role,
            "aria_label": aria_label,
            "name": name,
            "placeholder": placeholder,
            "value": value,
            "href": href,
            "onclick": onclick,
            "text": text,
            "label_text": label_text
        }

        current_checkbox.append(data)

        for l in range(clickables.count()):
            if i == l:
                continue
            click2 = clickables.nth(l)
            name2 = click2.get_attribute("name")
            if name != name2:
                continue
            tag2 = click2.evaluate("el => el.tagName.toLowerCase()")
            element_id2 = click2.get_attribute("id")
            element_type2 = click2.get_attribute("type")
            role2 = click2.get_attribute("role")
            aria_label2 = click2.get_attribute("aria-label")
            name2 = click2.get_attribute("name")
            placeholder2 = click2.get_attribute("placeholder")
            value2 = click2.get_attribute("value")
            href2 = click2.get_attribute("href")
            onclick2 = click2.get_attribute("onclick")
            text2 = click2.text_content() or ""
            label_text2 = ""
            if element_id2:
                label2 = page.locator(f'[for="{element_id2}"]')
                if label2.count() > 0:
                    label_text2 = label2.text_content() or ""
            data2 = {
                "tag": tag2,
                "index": l,
                "element_id": element_id2,
                "element_type": element_type2,
                "role": role2,
                "aria_label": aria_label2,
                "name": name2,
                "placeholder": placeholder2,
                "value": value2,
                "href": href2,
                "onclick": onclick2,
                "text": text2,
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
            state["cookies_response"]["action"] = "error"
            action = state["cookies_response"]["action"]

        state["current_page"]["url"] = page.url

    return state

def get_all_select(state: ApplicationState):
    page = state["current_page"]["page"]
    clickables = page.locator("select")

    select_elements = []

    for i in range(clickables.count()):
        click = clickables.nth(i)

        tag = click.evaluate("el => el.tagName.toLowerCase()")
        element_id = click.get_attribute("id")
        element_type = click.get_attribute("type")
        role = click.get_attribute("role")
        aria_label = click.get_attribute("aria-label")
        name = click.get_attribute("name")
        placeholder = click.get_attribute("placeholder")
        value = click.get_attribute("value")
        href = click.get_attribute("href")
        onclick = click.get_attribute("onclick")
        text = click.text_content() or ""

        label_text = ""
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.first.text_content() or ""

        options = click.locator("option")
        current_options = []

        for l in range(options.count()):
            option = options.nth(l)

            option_tag = option.evaluate("el => el.tagName.toLowerCase()")
            option_value = option.get_attribute("value")
            option_text = option.text_content() or ""

            option_data = {
                "tag": option_tag,
                "index": l,
                "value": option_value,
                "text": option_text
            }

            current_options.append(option_data)

        data = {
            "tag": tag,
            "index": i,
            "element_id": element_id,
            "element_type": element_type,
            "role": role,
            "aria_label": aria_label,
            "name": name,
            "placeholder": placeholder,
            "value": value,
            "href": href,
            "onclick": onclick,
            "text": text,
            "label_text": label_text,
            "options": current_options
        }

        select_elements.append({
            "grouping": name,
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

        tag = click.evaluate("el => el.tagName.toLowerCase()")
        element_id = click.get_attribute("id")
        element_type = click.get_attribute("type")
        role = click.get_attribute("role")
        aria_label = click.get_attribute("aria-label")
        name = click.get_attribute("name")
        placeholder = click.get_attribute("placeholder")
        value = click.get_attribute("value")
        href = click.get_attribute("href")
        onclick = click.get_attribute("onclick")
        text = click.text_content() or ""

        label_text = ""
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                label_text = label.first.text_content() or ""

        current_options = []

        list_id = click.get_attribute("list")

        if list_id:
            datalist = page.locator(f'datalist[id="{list_id}"]')

            if datalist.count() > 0:
                options = datalist.first.locator("option")

                for l in range(options.count()):
                    option = options.nth(l)

                    option_tag = option.evaluate("el => el.tagName.toLowerCase()")
                    option_value = option.get_attribute("value")
                    option_text = option.text_content() or ""

                    option_data = {
                        "tag": option_tag,
                        "index": l,
                        "value": option_value,
                        "text": option_text
                    }

                    current_options.append(option_data)

        data = {
            "tag": tag,
            "index": i,
            "element_id": element_id,
            "element_type": element_type,
            "role": role,
            "aria_label": aria_label,
            "name": name,
            "placeholder": placeholder,
            "value": value,
            "href": href,
            "onclick": onclick,
            "text": text,
            "label_text": label_text,
            "options": current_options
        }

        datalist_elements.append({
            "grouping": name,
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

state = front_page_elements({}, url)
print(state["current_page"])

print("Hello")

def opening_page(state: ApplicationState):
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_content()
        page = browser.new_page()
        page.goto(url)
        state["current_page"]["page"] = page
        state["current_page"]["url"] = page.url
        state["current_page"]["browser"] = browser
        state["current_page"]["context"] = context



from langgraph.graph import StateGraph, START, END

graph = StateGraph(ApplicationState)

graph.add_node("opening_page", opening_page)
graph.add_node("decide_page", decide_page)
graph.add_node("apply_process", apply_process)
graph.add_node("cookies_process", cookies_process)