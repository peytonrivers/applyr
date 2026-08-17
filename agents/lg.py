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
from datetime import datetime
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess, AITokens, QuestionProcess, AnswerItem, MarkdownProcess, ReviewMarkdownProcess, ReviewClickAndViewProcess, FindIcon
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

import pyautogui
from langchain_ollama import ChatOllama

from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END

graph = StateGraph(ApplicationState)
 

import time
import os
import psutil
from dotenv import load_dotenv
load_dotenv()

memory = psutil.virtual_memory()
openai_key = os.getenv("OPENAI_KEY")
MODEL_NAME = "gpt-5.4-nano"
MODEL_NAME2 = "gpt-5.6-luna"
llm = ChatOpenAI(model=MODEL_NAME, temperature = 0.3, api_key=openai_key)
llm2 = ChatOpenAI(model=MODEL_NAME2, temperature = 0.1, reasoning={"effort": "high"} ,api_key=openai_key)
structured_llm = llm.with_structured_output(ClickAction, include_raw=True)
multiple_question_llm = llm.with_structured_output(MultipleQuestion, include_raw=True)
all_elements_llm = llm.with_structured_output(AllElements, include_raw=True)
new_cookies_process_llm = llm.with_structured_output(NewCookiesProcess, include_raw=True)
cookies_process_llm = llm.with_structured_output(CookiesProcess, include_raw=True)
decide_page_llm = llm.with_structured_output(DecidePage, include_raw=True)
apply_process_llm = llm.with_structured_output(ApplyProcess, include_raw=True)
signup_process_llm = llm.with_structured_output(SignupProcess, include_raw=True)
forms_action_llm = llm.with_structured_output(FormsAction, include_raw=True)
question_process_llm2 = llm2.with_structured_output(QuestionProcess, include_raw=True)
markdown_process_llm2 = llm2.with_structured_output(MarkdownProcess, include_raw=True)
review_markdown_process_llm2 = llm2.with_structured_output(ReviewMarkdownProcess, include_raw=True)
review_click_and_view_process_llm2 = llm2.with_structured_output(ReviewClickAndViewProcess, include_raw=True)
find_icon_process_llm2 = llm2.with_structured_output(FindIcon, include_raw=True)
url = "https://jobs.fidelity.com/en/jobs/2132114/leap-software-engineer/"
url = "https://www.allstate.jobs/job/23527822/senior-product-engineer-software-java-/"
# url = "https://www.allstate.jobs/job/23283268/-net-senior-software-engineer/"
url = "https://www.allstate.jobs/job/23473343/cloud-services-lead-software-engineer/"
url = "https://www.allstate.jobs/job/23613565/java-development-lead-systems-engineer/"
print(url.title)
input_cost = 0.20 / 1000000
output_cost = 1.25 / 1000000
cached_cost = 0.02 / 1000000

def ai_token_tracker(new_tokens: dict, state: ApplicationState):
    token_usage = state["token_usage"]
    print(f"Token usage: {token_usage}")
    tracker = token_usage["tracker"] 
    tracker += 1
    print(f"New count: {tracker}")
    input_tokens = token_usage['input_tokens']
    cached_tokens = token_usage["cached_tokens"]
    output_tokens = token_usage["output_tokens"]
    total_cost = token_usage["total_cost"]
    new_input_tokens = new_tokens["input_tokens"]
    new_cached_tokens = new_tokens["input_token_details"]["cache_read"]
    print(f"new input token details: {new_tokens["input_token_details"]}")
    print(f"new cached tokens: {new_cached_tokens}")
    after_new_input_tokens = new_input_tokens - new_cached_tokens
    print(new_input_tokens)
    new_output_tokens = new_tokens["output_tokens"]
    print(new_output_tokens)
    input_tokens += after_new_input_tokens
    print(f"Total input tokens: {input_tokens}")
    cached_tokens += new_cached_tokens
    print(f"Total cached tokens: {cached_tokens}")
    output_tokens += new_output_tokens
    print(f"Total output tokens: {output_tokens}")
    total = (input_tokens * input_cost) + (cached_tokens * cached_cost) +(output_tokens * output_cost)
    state["token_usage"] = {
        "tracker": tracker,
         "input_tokens": input_tokens,
         "cached_tokens": cached_tokens,
         "output_tokens": output_tokens,
         "total_cost": total
    }
    print(f"Total ${total}")
    return state

def coordinates_process(coordinates: list, full_page_width, full_page_height):
    x1 = coordinates[0]
    y1 = coordinates[1]
    x2 = coordinates[2]
    y2 = coordinates[3]
    middle_x = (x1 + x2) / 2
    middle_y = (y1 + y2) / 2
    page_x = (middle_x * full_page_width)
    page_y = (middle_y * full_page_height)
    return page_x, page_y

def time_coordinates_process(coordinates: list, full_page_width, full_page_height):
    x1 = coordinates[0]
    y1 = coordinates[1]
    x2 = coordinates[2]
    y2 = coordinates[3]
    middle_x = (x1 + x2) / 2
    left_y = (y1 + y2) / 2
    left_x = (x1 * full_page_width)
    page_y = (left_y * full_page_height)
    page_x = (middle_x * full_page_width)
    print(f"Time coordinates, x: {left_x}, y: {page_y}")
    print(f"Regular coordinates, x: {page_x}, y: {page_y}")
    return left_x, page_y

def page_loaded(state: ApplicationState):
    page = state["current_page"]["page"]
    for i in range(7):
        time.sleep(3)
        body_text = page.locator("body").inner_text()
        if len(body_text) >= 5:
            return True
    return False

def screenshot_process(state: ApplicationState):
    page = state["current_page"]["page"]
    print(page)
    page.wait_for_load_state("load")
    page_loaded(state=state)
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    page.set_viewport_size({"width": full_page_width, "height": full_page_height})
    screenshot = page.screenshot()
    encoded_bytes = base64.b64encode(screenshot).decode("utf-8")
    return encoded_bytes

def omniparser_process(state: ApplicationState):
    encoded_bytes = screenshot_process(state)
    print(f"encoded bytes type: {type(encoded_bytes)})")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    response_data = response.json()
    encoded_bytes = response_data["encoded_bytes"]
    boxes_details = response_data["boxes_details"]
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image.show()
    print(f"Boxes details: {boxes_details}")
    time.sleep(10)
    return encoded_bytes, boxes_details


def decide_page(state: ApplicationState):
    encoded_bytes = screenshot_process(state)
    prompt = """Your an AI Application Helper and your job is to decide what page this is
    1. cookies - You always choose this page if there are cookies on the page
    2. apply - You choose this page if we need to click apply now, apply manually, or we only need to click one buttton to continue
    3. forms - You choose this page if there is forms that need to be filled
    4. verification - You choose this page if there is a verification code that needs to be filled out, or if you need to verify an email, anything to do with verifying an account.
    5. exit - You choose this page if there the url isn't active or we have finished the job application.
    6. wait - if the page hasn't loaded you choose this process, usually you can tell based off there being nothing on the screen but not if there's an error present.

    If cookies are present always choose the cookies option.
    """
    response = decide_page_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_bytes}"
                    }
                }
            ]
        }
    ])
    details = response["raw"]
    decision = response["parsed"]
    new_tokens = details.usage_metadata
    action = decision["action"]
    state["action"] = action

    state = ai_token_tracker(new_tokens, state)

    print(f"AI Tokens: {new_tokens}")
    print(f"AI details: {details}")
    print(f"AI decision: {decision}")
    print(f"decide page memory pecent: {memory.percent}%")
    return state

def decide_routing(state: ApplicationState):
    action = state["action"]
    print(f"Decide routing action: {action}")
    if action == "apply":
        return "apply"
    if action == "cookies":
        return "cookies"
    elif action == "signup":
        return "signup"
    elif action == "forms":
        return "forms"
    elif action == "application":
        return "application"
    elif action == "verification":
        return "verification"
    elif action == "wait":
        return "wait"
    else:
        # Fallback for "error" or any unexpected value
        return "exit" 

def wait_process(state: ApplicationState):
    time.sleep(20)
    return state

def cookies_process(state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details = omniparser_process(state)
    prompt = f"""
You are an AI Applicant Helper.

Your job is to examine the screenshot and the detected interface elements, then identify the single icon that accepts or confirms the website's cookie consent prompt.

You will receive:
1. A screenshot of the webpage.
2. Detected interface elements in `boxes_details`.

Use BOTH the screenshot and `boxes_details` to make your decision.

Boxes details:
{boxes_details}

INSTRUCTIONS

- Select exactly one icon.
- Only select an element that belongs to a cookie consent banner, cookie popup, privacy popup, or consent-management dialog.
- Prefer the option that accepts all cookies or allows the user to continue without opening additional settings.
- Use nearby text and the visual layout to determine whether a button belongs to the cookie prompt.
- A generic button such as "Continue," "Yes," or "OK" should only be selected when the surrounding context clearly relates to cookies or privacy consent.
- Do not select buttons from the job application, account creation form, navigation bar, advertisements, or unrelated popups.
- Do not select links that only open the cookie policy or privacy policy.
- Do not select "Manage Preferences," "Cookie Settings," or "Customize" when a direct acceptance option is available.
- Do not select the close icon when an acceptance button is available.
- Do not guess when no cookie consent control is visible.

PREFERRED OPTIONS

Choose options in approximately this priority order:

1. Accept All Cookies
2. Accept All
3. Allow All
4. Agree and Continue
5. I Agree
6. Accept
7. Allow
8. Yes
9. OK
10. Continue

anything that you think based on the picture and boxes is how we accept the  cookies!!!

AVOID OPTIONS SUCH AS

- Reject All
- Decline
- Deny
- Necessary Cookies Only
- Manage Preferences
- Cookie Settings
- Customize
- Learn More
- Privacy Policy
- Cookie Policy
- Close

OUTPUT FORMAT

Return:

icon: <integer icon number>
icon_reason: <brief explanation>

Example:

icon: 37
icon_reason: Icon 37 says "Accept All Cookies" and is located inside the cookie consent popup.

Example if no cookies are present:
icon: None
icon_reason: there are no cookies present on this screen
"""

    ai_response = cookies_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                ]}])
    details = ai_response["raw"]
    new_tokens = details.usage_metadata
    decision = ai_response["parsed"]
    print(f"AI Decision: {decision}")
    icon = decision.get("icon")
    if not icon:
        return state
    icon_reason = decision.get("icon_reason")
    cookies_action(icon, boxes_details, state)
    print(f"icon: {icon}")
    print(f"icon reason: {icon_reason}")
    return state


def cookies_action(icon: int, boxes_details: json, state: ApplicationState):
    page = state["current_page"]["page"]
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    clickable_item = boxes_details[icon]
    coordinates = clickable_item["bbox"]
    x1 = coordinates[0]
    y1 = coordinates[1]
    x2 = coordinates[2]
    y2 = coordinates[3]
    middle_x = (x1 + x2) / 2
    middle_y = (y1 + y2) / 2
    page_x = (middle_x * full_page_width)
    page_y = (middle_y * full_page_height)
    print(f"Clickable item: {clickable_item}")
    print(f"Coordinates: {coordinates}")
    try:
        with page.expect_popup() as new_page:
            page.mouse.click(page_x, page_y)
        new_page.wait_for_load_state("domcontentloaded")
        new_page = new_page.value
        url = new_page.url
        state["current_page"] = {
            "page": new_page,
            "url": url
        }
        time.sleep(5)
    except Exception:
        page.wait_for_load_state("domcontentloaded")
        time.sleep(5)
    return state


def apply_process(state: ApplicationState):
    print(f"Apply process checkpoint 1")
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details = omniparser_process(state)
    prompt = f"""
You are an AI Applicant Helper.

Your goal is to start or continue the job application process.

You will receive:
1. A screenshot of the webpage.
2. The detected interface elements (`boxes_details`).

Use BOTH the screenshot and `boxes_details` to determine which icon should be clicked.

boxes_details:
{boxes_details}

INSTRUCTIONS

- Find the single best icon that advances the user into the application.
- Always prefer applying directly on the employer's website.
- If both "Apply Manually" and "Easy Apply" (or similar) are available, ALWAYS choose "Apply Manually."
- If an application has already been started, prefer buttons that continue the existing application.

Highest priority button text includes:
- Apply Manually
- Continue Application
- Continue
- Resume Application
- Finish Application
- Start Application
- Apply Now
- Apply
- Begin Application
- Start

Ignore buttons or links such as:
- Sign In
- Log In
- Register
- Learn More
- Save Job
- Share
- Follow
- Company Page
- View Similar Jobs
- Back
- Cancel
- Close
- Report Job
- Contact
- Help

Do not click advertisements, navigation menus, social media links, or unrelated page controls.

Use the screenshot as additional context whenever the detected text is incomplete.

OUTPUT

Return:

icon: <icon number>
icon_reason: <brief explanation>

Example:

icon: 17
icon_reason: The button says "Apply Manually," which is the preferred way to begin the application.

Example for no application button found:

icon: None
icon_reason: There is no apply button found on the screen.
"""
    response = apply_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                ]}])
    print(f"Apply process checkpoint 3")
    details = response["raw"]
    decision = response["parsed"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    icon = decision.get("icon")
    if not icon:
        return state
    print(icon)
    icon_reason = decision["icon_reason"]
    print(icon_reason)
    state = apply_action(icon=icon, boxes_details=boxes_details, state=state)
    return state
    
def apply_action(icon: int, boxes_details: json, state: ApplicationState):
    page = state["current_page"]["page"]
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    clickable_item = boxes_details[icon]
    coordinates = clickable_item["bbox"]
    x1 = coordinates[0]
    y1 = coordinates[1]
    x2 = coordinates[2]
    y2 = coordinates[3]
    middle_x = (x1 + x2) / 2
    middle_y = (y1 + y2) / 2
    page_x = (middle_x * full_page_width)
    page_y = (middle_y * full_page_height)
    print(f"Clickable item: {clickable_item}")
    print(f"Coordinates: {coordinates}")
    print(f"Playwright coordinates x: {page_x}, y: {page_y}")
    try:
        with page.expect_popup() as new_page:
            page.mouse.click(page_x, page_y)
        print(f"old page: {page}")
        new_page = new_page.value
        print(f"new page: {new_page}")
        new_page.wait_for_load_state("domcontentloaded")
        url = new_page.url
        print(f"old current page: {state["current_page"]}")
        state["current_page"] = {
            "page": new_page,
            "url": url
        }
        print(f"new current page: {state["current_page"]}")
        time.sleep(5)
    except Exception:
        page.wait_for_load_state("domcontentloaded")
        time.sleep(5)
    return state

# The marking to where to put the old signup process

# The marking to where the new signup process
def answser_question_process(state: ApplicationState):
    encoded_bytes, boxes_details = omniparser_process(state=state)
    prompt = f"""
You're an AI Applicant Helper who is currently in the forms process.

You're job is to look at the current forms page and to have these responsibilities.
1. Answer Every Required Question
2. Look at any error's on the page and do your best to handle them
3. Answer every question by using two things: the user's profile and common sense
4. Make sure to use common sense while filling out this form
5. Use common sense, if we have already answered the required questions and the answers are correct, we can just continue to the next.

You will answer every question with 1 of these 10 actions.

Immediate Action Section

1. skip - when you want to skip a question, make sure you list every question you skip.

2. fill - when you want to fill out a question

3. fill_with_time - used when you want to fill out an element that requires a time or date value.

4. delete - used when you want to delete the given text

5. delete_and_fill - used when you want to delete the given text and then fill it out with new information

6. click - when you want to click or unclick an element


Process Action Section

7. upload_resume - Used when the current question requires the user's resume file to be uploaded.

8. upload_cover_letter - Used when the current question requires the user's cover letter file to be uploaded.

9. click_and_view - Used when clicking an element will reveal or load additional information, questions, fields, or a new section that must be analyzed before continuing. Only use click and view when you know that you need to fill out more information, not just when you want to see what's behind a button or element.

10. markdown - Used when clicking an element opens a list of selectable options, such as a dropdown, combobox, menu, or similar selection component. The markdown process is responsible for opening the element, discovering the available options, and selecting the correct option.

11. submit - Used for buttons that finalize the current page or section, such as Submit, Save and Continue, Continue, Next, or similar progression buttons.


Look at the boxes details and the image to help you determine which icon we are looking at.

boxes_details: {boxes_details}

Within the icon's you pick, pick the icon that chooses the option and not the question if possible.

Ex 1:
{{
    action: skip,
    reason: This question has already been filled out correctly and does not require any action.
}}

Ex 2:
{{
    action: fill,
    action_text: {state["email"]}
    icon: 28,
    reason: This question asks for the user's email address, so the email input should be filled with {state["email"]} from the User Profile Section.
}}

Ex 3:
{{
    action: fill_with_time,
    action_text: 08/01/2020,
    icon: 35,
    reason: This question asks for a time, so the time input should be filled with the user's answer.
}}

Ex 4:
{{
    action: delete,
    icon: 38,
    reason: This input contains incorrect information and should be cleared with the correct answer in the User Profile Section.
}}

Ex 5:
{{
    action: delete_and_fill,
    action_text: {state["first_name"]},
    icon: 42,
    reason: The current first name is incorrect, so the existing value should be deleted and replaced with {state["first_name"]} due to me checking the User Profile Section.
}}

Ex 6:
{{
    action: click,
    icon: 32,
    reason: This question asks whether the user is a U.S. citizen and Yes due to the User Profile Section.
}}

Ex 7:
{{
    action: upload_resume,
    icon: 50,
    reason: This question requires the user's resume to be uploaded and there is a resume to be uploaded in the User Profile Section.
}}

Ex 8:
{{
    action: upload_cover_letter,
    icon: 52,
    reason: This question requires the user's cover letter to be uploaded and there is a cover letter to be uploaded in the User Profile Section.
}}

Ex 9:
{{
    action: click_and_view,
    icon: 22,
    question: Add More Work Experience,
    reason: The user has one more work experience that needs to be uploaded due to the User Profile Section showing two work experience.
}}

Ex 10:
{{
    action: markdown,
    icon: 60,
    current_question: What U.S. State are you in?,
    reason: This question uses a dropdown with multiple selectable state options. The markdown process should open the element, discover the available options, and determine which option matches the user's information, I answered this through the User Profile Section.
}}

Ex 11:
{{
    action: submit,
    icon: 30,
    reason: This is the Submit, Save and Continue, Continue, or Next button that progresses from the current page or section.
}}

USER PROFILE Section:

Account information:
- User ID: {state["user_id"]}
- Email: {state["email"]}
- Password: {state["password"]}

Personal information:
- First name: {state["first_name"]}
- Last name: {state["last_name"]}
- Preferred name: None
- Phone number: {state["phone_number"]}

Address:
- Address line 1: {state["address_line1"]}
- Address line 2: {state["address_line2"]}
- City: {state["city"]}
- State: {state["user_state"]}
- ZIP code: {state["zip_code"]}
- Country: {state["country"]}
- date: {state["date"]}

Extra details:
- how this job was found: other or another website or something close to other or another website.

Employment eligibility:
- Authorized to work in the United States: {state["work_authorized"]}
- Requires current or future employment sponsorship: {state["requires_sponsorship"]}

Voluntary self-identification:
- Veteran: {state["veteran"]}
- Disability: {state["disability"]}

Work Experience: {state["work_experience"]}
Education: {state["education"]}

Professional links:
- LinkedIn: {state["linkedin_url"]}
- GitHub: {state["github_url"]}
- Portfolio: {state["portfolio_url"]}


Resume: {state["resume_text"]}
Cover letter: {state["cover_letter_text"]}
"""

    response = question_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    answers = response["parsed"]
    ai_answers = answers["items"]
    print(f"AI Answers: {ai_answers}")
    state = action_process(ai_answers=ai_answers, boxes_details=boxes_details, state=state)
    return state

def action_process(ai_answers: list[dict], boxes_details: list[dict], state: ApplicationState):
    ai_answers.sort(key=lambda x: {"skip": 0, "fill": 1, "fill_with_time": 2, "delete": 3, "delete_and_fill": 4, "click": 5, "upload_resume": 6, "upload_cover_letter": 7, "markdown": 8, "click_and_view": 9, "submit": 10}.get(x["action"].lower(), 999))
    for i in range(len(ai_answers)):
        current_answer = ai_answers[i]
        action = current_answer.get("action")
        if not action or action == "skip":
            continue
        icon = current_answer.get("icon")
        if not icon:
            continue
        current_box = boxes_details[icon]
        state = execute_action(current_answer=current_answer, current_box=current_box, state=state)
        print(f"Action: {action}")
        print(f"State page after execution: {state["current_page"]["page"]}")
    return state

def find_icon(current_answer: dict, state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details = omniparser_process(state=state)
    prompt = f"""
You are an AI Applicant helper and will be helping us find the icon from the current_answer.
Look at the boxes_details to determine the icon we will be clicking.


current_answer: {current_answer}

boxes_details: {boxes_details}

Example output:
{{
icon: 48,
icon_reason: the same question on the current answer is pretty much the same text on this icon.
}}
"""
    response = find_icon_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    decision = response["parsed"]
    icon = decision.get("icon")
    current_box = boxes_details[icon]
    coordinates = current_box["bbox"]
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    return encoded_bytes, page_x, page_y, state

def execute_action(current_answer: dict, current_box: dict, state: ApplicationState):
    page = state["current_page"]["page"]
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    action = current_answer.get("action")
    if not action or action == "skip":
        return state
    icon = current_answer.get("icon")
    if not icon:
        return state
    coordinates = current_box.get("bbox")
    if not coordinates:
        return state
    page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    if action == "fill":
        action_text = current_answer.get("action_text")
        if not action_text:
            return state
        page.mouse.click(page_x, page_y)
        time.sleep(2)
        page.keyboard.type(action_text)
        time.sleep(1)
        return state
    if action == "fill_with_time":
        action_text = current_answer.get("action_text")
        if not action_text:
            return state
        page.mouse.click(page_x, page_y)
        page.keyboard.press("ArrowLeft")
        time.sleep(1)
        page.keyboard.type(action_text)
        time.sleep(1)
        return state
    if action == "click":
        page.mouse.click(page_x, page_y)
        time.sleep(2)
        return state
    if action == "markdown":
        screenshot = page.screenshot()
        old_bytes = base64.b64encode(screenshot).decode("utf-8")
        page.evaluate(f"window.scrollTo({page_x}, {page_y})")

        time.sleep(1)
        page.mouse.click(page_x, page_y)
        time.sleep(1)
        pyautogui.press("down")
        time.sleep(5)
        new_screenshot = page.screenshot()
        new_bytes = base64.b64encode(new_screenshot).decode("utf-8")
        body_text = page.locator("body").inner_text()
        state = markdown_process(current_answer=current_answer, old_bytes=old_bytes, new_bytes=new_bytes, body_text=body_text, page_x=page_x, page_y=page_y, state=state)

        time.sleep(5)
        print(f"Finished arrow process")
        return state
    if action == "click_and_view":
        encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        page.mouse.click(page_x, page_y)       
        state = click_and_view_process(current_answer=current_answer, old_bytes=encoded_bytes, state=state)
        time.sleep(1)
        return state
    if action == "submit":
        try:
            with page.expect_popup() as new_page:
                page.mouse.click(page_x, page_y)
            print(f"old page: {page}")
            new_page = new_page.value
            print(f"new page: {new_page}")
            new_page.wait_for_load_state("domcontentloaded")
            url = new_page.url
            print(f"old current page: {state["current_page"]}")
            state["current_page"] = {
                "page": new_page,
                "url": url
            }
            print(f"new current page: {state["current_page"]}")
            time.sleep(5)
            return state
        except Exception:
            page.wait_for_load_state("domcontentloaded")
            time.sleep(5)
            print(f"State after submit: {state}")
            return state
    return state

def row_change(matrix_image1, matrix_image2):
    for i in range(len(matrix_image1)):
        matrix_width1 = matrix_image1[i]
        matrix_width2 = matrix_image2[i]
        for l in range(len(matrix_width1)):
            elem1 = matrix_width1[l]
            elem2 = matrix_width2[l]
            for j in range(len(elem1)):
                num1 = elem1[j]
                num2 = elem2[j]
                if num1 != num2:
                    print(f"Row: {i+1}")
                    print(elem1)
                    print(elem2)
                    return i+1
        return None

def cropped_image_process(encoded_image1: str, encoded_image2: str):
    decoded_image1 = base64.b64decode(encoded_image1.encode("utf-8"))
    decoded_image2 = base64.b64decode(encoded_image2.encode("utf-8"))
    buffer1 = io.BytesIO(decoded_image1)
    buffer2 = io.BytesIO(decoded_image2)
    image1 = Image.open(buffer1)
    image1.show()
    image2 = Image.open(buffer2)
    image2.show()
    matrix_image1 = np.array(image1)
    matrix_image2 = np.array(image2)
    first_cropped_row = row_change(matrix_image1=matrix_image1, matrix_image2=matrix_image2)
    print(f"Firt cropped row: {first_cropped_row}")
    if not first_cropped_row:
        return None
    reversed_stage1 = reversed(matrix_image1)
    reversed_stage2 = reversed(matrix_image2)
    reversed_matrix_image1 = list(reversed_stage1)
    reversed_matrix_image2 = list(reversed_stage2)
    second_cropped_row = row_change(matrix_image1=reversed_matrix_image1, matrix_image2=reversed_matrix_image2)
    width_image2, height_image2 = image2.size
    final_second_cropped_row = height_image2 - second_cropped_row
    print(f"Final second cropped row: {final_second_cropped_row}")
    cropped_coordinates = (0, first_cropped_row, width_image2, final_second_cropped_row)
    cropped_image = image2.crop(cropped_coordinates)
    cropped_buffer = io.BytesIO()
    cropped_image.save(cropped_buffer, format="PNG")
    cropped_bytes = cropped_buffer.getvalue()
    encoded_cropped_bytes = base64.b64encode(cropped_bytes).decode("utf-8")
    data = {"image_input": encoded_cropped_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    response_data = response.json()
    encoded_bytes = response_data["encoded_bytes"]
    boxes_details = response_data["boxes_details"]
    return encoded_bytes, boxes_details

def markdown_process(current_answer: dict, old_bytes: str, new_bytes: str, body_text: str, page_x: float, page_y: float, state: ApplicationState):
    page = state["current_page"]["page"]

    for attempt in range(5):
        encoded_bytes, boxes_details = cropped_image_process(encoded_image1=old_bytes, encoded_image2=new_bytes)
        current_question = current_answer.get("current_question")
        prompt = f"""
You're an AI Applicant Helper that is in the markup process.

Markdown definition: markdown - Used when clicking an element opens a list of selectable options, such as a dropdown, combobox, menu, or similar selection component. The markdown process is responsible for opening the element, discovering the available options, and selecting the correct option.

You're goal is to look at the the body text + the image to find all the options for the question we are in.

current_question: {current_question}
body_text: {body_text}

You will showcase all the options with the text and the option number in order.
You will showcase the option choice you hope to click.
You will also showcase the current option that our keyboard is at, so we know how many times we need to use the keyboard to go up or down to click the option_choice.
Use the User Profile Section and common sense to help answer the markdown process.

USER PROFILE:

Account information:

- User ID: {state["user_id"]}
- Email: {state["email"]}
- Password: {state["password"]}

Personal information:

- First name: {state["first_name"]}
- Last name: {state["last_name"]}
- Preferred name: None
- Phone number: {state["phone_number"]}

Address:

- Address line 1: {state["address_line1"]}
- Address line 2: {state["address_line2"]}
- City: {state["city"]}
- State: {state["user_state"]}
- ZIP code: {state["zip_code"]}
- Country: {state["country"]}
- date: {state["date"]}

Extra details:
- how this job was found: other or another website or something close to other or another website.

Employment eligibility:

- Authorized to work in the United States: {state["work_authorized"]}
- Requires current or future employment sponsorship: {state["requires_sponsorship"]}

Voluntary self-identification:

- Veteran: {state["veteran"]}
- Disability: {state["disability"]}

Work Experience: {state["work_experience"]}
Education: {state["education"]}

Professional links:

- LinkedIn: {state["linkedin_url"]}
- GitHub: {state["github_url"]}
- Portfolio: {state["portfolio_url"]}
- Where we found this job: Always choose other or another website or the choice that best resembles the answer ['other', 'another website' or something that is close.]

Example output 1:
options: [
{{
text: Alabama,
option_number: 1
}},
{{
text: Alaska,
option_number: 2
}},
{{
text: Arkansas,
option_number: 3
}},
{{
text: California,
option_number: 4
}}
]

option_choice: 3

current_option: 1

option_reason: We are at the 1st highlighted option in the photo and we need to go to the third option to be correct

Example 2:
options: [
{{
text: Alabama,
option_number: 1
}},
{{
text: Alaska,
option_number: 2
}},
{{
text: Arkansas,
option_number: 3
}},
{{
text: California,
option_number: 4
}}
]

option_choice: 3

current_option: 0

option_reason: There is currently no highlighted option in the photo and we need to move to the third option
"""

        response = markdown_process_llm2.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                ]
            }
        ])

        details = response["raw"]
        new_tokens = details.usage_metadata

        state = ai_token_tracker(
            new_tokens=new_tokens,
            state=state
        )

        decision = response["parsed"]

        print(f"Markdown decision: {decision}")

        options = decision["options"]
        option_choice = decision["option_choice"]
        current_option = decision["current_option"]

        arrow_count = option_choice - current_option

        print(f"How many times we need to move the arrow: {arrow_count}")

        pyautogui.moveTo(500, 500, duration=0.2)

        if arrow_count == 0:
            pyautogui.press("up")
            pyautogui.press("down")
            pyautogui.press("enter")

        elif arrow_count < 0:
            for i in range(abs(arrow_count)):
                pyautogui.press("up")

            pyautogui.press("enter")

        elif arrow_count > 0:
            for i in range(arrow_count):
                pyautogui.press("down")
                print(f"Arrow down: {i+1}")
                time.sleep(1)

            pyautogui.press("enter")
        time.sleep(5)

        markdown_status, state = review_markdown_process(
        current_answer=current_answer,
            body_text=body_text,
            page_x=page_x,
            page_y=page_y,
            state=state
        )

        if markdown_status == "correct":
            return state

        elif markdown_status == "more_questions":
            return state

        elif markdown_status == "incorrect_and_box_closed":
            page.mouse.click(page_x, page_y)
            body_text = page.locator("body").inner_text()
            continue

        elif markdown_status == "incorrect_and_box_open":
            body_text = page.locator("body").inner_text()
            continue

        elif markdown_status == "more_markdown":
            body_text = page.locator("body").inner_text()
            continue

        else:
            return state

    return state

def review_markdown_process(current_answer: dict, body_text: str, page_x: float, page_y: float, state: ApplicationState):
    time.sleep(2)
    page = state["current_page"]["page"]
    encoded_bytes = screenshot_process(state=state)
    prompt = f"""
You're an AI Applicant helper that's goal is to help answer questions on behalf of the user.

Your specific task is Markdown reviewer.

Markdown definition: markdown - Used when clicking an element opens a list of selectable options, such as a dropdown, combobox, menu, or similar selection component. The markdown process is responsible for opening the element, discovering the available options, and selecting the correct option.

You will look at the current question and the answer and determine one of four things.
1. correct - the information is correct and fully completed.
2. incorrect - the answer inputted is wrong based on the User Profile.
4. more markdown process - after the first step of the markdown process, there is another markdown process that needs to be done.
5. more questions - after the first step of the markdown process, user inputs formed that need to be handled by the regular answer question process.

Look at the current answer and specifically the current question to see determine your markdown_status!

You only look at the current question markdown process and no other question on the page to determine the markdown_status.

current_answer {current_answer}

EX 1:
{{
markdown_status: correct,
reason: state listed is correct based on the user profile on the question.
}}

Ex 2:
{{
markdown_status: incorrect_and_box_open
reason: We have inputted the wrong answer even though it says the user is from: {state["user_state"]} due to the User Profile. The box is still open on the current question.
}}

Ex 3:
{{
markdown_status: incorrect_and_box_closed
reason: We have inputted the wrong answer even though it says the user is from: {state["user_state"]} due to the User Profile. The box is closed on the current question.
}}

Ex 4:
{{
markdown_status: more_markdown
reason: After the first step there is another button that is loaded that we need to answer on the current question.
}}

Ex 5:
{{
markdown_status: more_questions
reason: After the first step it appears a text box has loaded and needs to be sent to the more questions process through the current question. 
}}


USER PROFILE:

Account information:
- User ID: {state["user_id"]}
- Email: {state["email"]}
- Password: {state["password"]}

Personal information:
- First name: {state["first_name"]}
- Last name: {state["last_name"]}
- Preferred name: {state["preferred_name"]}
- Phone number: {state["phone_number"]}

Address:
- Address line 1: {state["address_line1"]}
- Address line 2: {state["address_line2"]}
- City: {state["city"]}
- State: {state["user_state"]}
- ZIP code: {state["zip_code"]}
- Country: {state["country"]}
- date: {state["date"]}

Employment eligibility:
- Authorized to work in the United States: {state["work_authorized"]}
- Requires current or future employment sponsorship: {state["requires_sponsorship"]}

Work Experience: {state["work_experience"]}
Education: {state["education"]}

Voluntary self-identification:
- Veteran: {state["veteran"]}
- Disability: {state["disability"]}

Professional links:
- LinkedIn: {state["linkedin_url"]}
- GitHub: {state["github_url"]}
- Portfolio: {state["portfolio_url"]}
- Where we found this job: Always choose other or another website or the choice that best resembles the answer ['other', 'another website' or something that is close.]


Resume: {state["resume_text"]}
Cover letter: {state["cover_letter_text"]}
"""
    response = review_markdown_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    decision = response["parsed"]
    print(f"Markdown decision: {decision}")
    markdown_status = decision["markdown_status"]
    return markdown_status, state

def click_and_view_process(
    current_answer: dict,
    old_bytes: str,
    state: ApplicationState
):
    page = state["current_page"]["page"]

    for attempt in range(5):

        print(f"Click and view attempt: {attempt + 1}")

        encoded_bytes, boxes_details = omniparser_process(
            state=state
        )

        current_question = current_answer.get("question")

        prompt = f"""
You're an AI Applicant Helper that is currently inside of the
Click and View Process.

CLICK AND VIEW DEFINITION:

click_and_view is used when clicking an element reveals additional
information, questions, fields, or a new section that must be completed.

Your job is to handle ONLY the questions that appeared as a result of
the original click_and_view action.

CURRENT CLICK AND VIEW QUESTION:

{current_question}


IMPORTANT SCOPE RULE:

You are being given TWO images.

IMAGE 1:
The page BEFORE the click_and_view element was clicked.

IMAGE 2:
The CURRENT page after the click_and_view element was clicked.

Compare the two images.

ONLY answer questions, inputs, buttons, dropdowns, checkboxes, or
other elements that belong to the section revealed by:

{current_question}

IGNORE every unrelated question that already existed before
the click_and_view action.

Even if another question on the page is required, DO NOT answer it
unless it belongs to the current click_and_view section.


You have the same actions available as the regular
answer question process.


Immediate Action Section

1. skip
- The question inside the current click_and_view section is already
  correctly completed.

2. fill
- Fill a normal text input inside the current click_and_view section.

3. fill_with_time
- Fill an input requiring a date or time.

4. delete
- Delete incorrect existing text.

5. delete_and_fill
- Delete incorrect text and replace it.

6. click
- Click or unclick an element.


Process Action Section

7. upload_resume
- Upload the resume if the CURRENT revealed section specifically
  requests it.

8. upload_cover_letter
- Upload the cover letter if the CURRENT revealed section specifically
  requests it.

9. click_and_view
- Another element inside the CURRENT revealed section needs to reveal
  additional required questions.

10. markdown
- A dropdown, combobox, menu, or selectable list inside the CURRENT
  revealed section needs to be answered.

11. submit
- A Save, Done, Continue, Add, Confirm, or similar button specifically
  belonging to the CURRENT revealed section needs to be clicked.


boxes_details:

{boxes_details}


IMPORTANT:

Do NOT use buttons such as the application's main Continue or Submit
button unless that button specifically belongs to the current
click_and_view section.

For example:

If current_question is:

"Add More Work Experience"

Then you should ONLY worry about things such as:

- Company
- Position
- Start Date
- End Date
- Description
- Save Experience

that appeared because Add More Work Experience was clicked.

Do NOT suddenly answer unrelated address, demographic, eligibility,
education, or other questions elsewhere on the application.

Ex 1:
{{
    action: skip,
    reason: This question has already been filled out correctly and does not require any action.
}}

Ex 2:
{{
    action: fill,
    action_text: {state["email"]}
    icon: 28,
    reason: This question asks for the user's email address, so the email input should be filled with {state["email"]} from the User Profile Section.
}}

Ex 3:
{{
    action: fill_with_time,
    action_text: 08/01/2020,
    icon: 35,
    reason: This question asks for a time, so the time input should be filled with the user's answer.
}}

Ex 4:
{{
    action: delete,
    icon: 38,
    reason: This input contains incorrect information and should be cleared with the correct answer in the User Profile Section.
}}

Ex 5:
{{
    action: delete_and_fill,
    action_text: {state["first_name"]},
    icon: 42,
    reason: The current first name is incorrect, so the existing value should be deleted and replaced with {state["first_name"]} due to me checking the User Profile Section.
}}

Ex 6:
{{
    action: click,
    icon: 32,
    reason: This question asks whether the user is a U.S. citizen and Yes due to the User Profile Section.
}}

Ex 7:
{{
    action: upload_resume,
    icon: 50,
    reason: This question requires the user's resume to be uploaded and there is a resume to be uploaded in the User Profile Section.
}}

Ex 8:
{{
    action: upload_cover_letter,
    icon: 52,
    reason: This question requires the user's cover letter to be uploaded and there is a cover letter to be uploaded in the User Profile Section.
}}

Ex 9:
{{
    action: click_and_view,
    icon: 22,
    question: Add More Work Experience,
    reason: The user has one more work experience that needs to be uploaded due to the User Profile Section showing two work experience.
}}

Ex 10:
{{
    action: markdown,
    icon: 60,
    current_question: What U.S. State are you in?,
    reason: This question uses a dropdown with multiple selectable state options. The markdown process should open the element, discover the available options, and determine which option matches the user's information, I answered this through the User Profile Section.
}}

Ex 11:
{{
    action: submit,
    icon: 30,
    reason: This is the Submit, Save and Continue, Continue, or Next button that progresses from the current page or section.
}}

USER PROFILE:

Account information:
- User ID: {state["user_id"]}
- Email: {state["email"]}
- Password: {state["password"]}

Personal information:
- First name: {state["first_name"]}
- Last name: {state["last_name"]}
- Preferred name: None
- Phone number: {state["phone_number"]}

Address:
- Address line 1: {state["address_line1"]}
- Address line 2: {state["address_line2"]}
- City: {state["city"]}
- State: {state["user_state"]}
- ZIP code: {state["zip_code"]}
- Country: {state["country"]}
- Date: {state["date"]}

Employment eligibility:
- Authorized to work in the United States: {state["work_authorized"]}
- Requires sponsorship: {state["requires_sponsorship"]}

Voluntary self-identification:
- Veteran: {state["veteran"]}
- Disability: {state["disability"]}

Work Experience: {state["work_experience"]}
Education: {state["education"]}

Professional links:
- LinkedIn: {state["linkedin_url"]}
- GitHub: {state["github_url"]}
- Portfolio: {state["portfolio_url"]}

Resume:
{state["resume_text"]}

Cover Letter:
{state["cover_letter_text"]}
"""

        response = question_process_llm2.invoke([
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{old_bytes}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_bytes}"
                        }
                    }
                ]
            }
        ])

        details = response["raw"]
        new_tokens = details.usage_metadata

        state = ai_token_tracker(
            new_tokens=new_tokens,
            state=state
        )

        answers = response["parsed"]
        ai_answers = answers["items"]

        print(f"Click and view answers: {ai_answers}")

        state = action_process(
            ai_answers=ai_answers,
            boxes_details=boxes_details,
            state=state
        )

        click_and_view_status, state = review_click_and_view_process(
            current_answer=current_answer,
            old_bytes=old_bytes,
            state=state
        )

        if click_and_view_status == "complete":
            print("Click and view process complete")
            return state

        elif click_and_view_status == "more_questions":
            print("More click and view questions remain")
            continue

        elif click_and_view_status == "incorrect":
            print("Click and view contains incorrect information")
            continue

        else:
            return state

    return state

def review_click_and_view_process(
    current_answer: dict,
    old_bytes: str,
    state: ApplicationState
):
    time.sleep(2)

    encoded_bytes = screenshot_process(state=state)

    current_question = current_answer.get("question")

    prompt = f"""
You're an AI Applicant Helper.

Your specific task is Click and View Reviewer.

CLICK AND VIEW DEFINITION:

click_and_view is used when clicking an element reveals additional
information, questions, fields, or a new section that needs to be
completed.

The original click_and_view question was:

{current_question}


You are given:

IMAGE 1:
The page BEFORE the click_and_view action happened.

IMAGE 2:
The CURRENT page.

Compare these images and review ONLY the section associated with:

{current_question}


You must choose one of THREE statuses:


1. complete

The click_and_view process is fully completed.

All required questions that appeared because of the click_and_view
action have been answered correctly.

The section may also have been successfully saved and closed.


2. more_questions

The click_and_view section is NOT finished.

There are still unanswered required questions, newly revealed
questions, dropdowns, checkboxes, inputs, or buttons that need to
be handled.

This includes new questions that appeared because of a previous
answer inside the click_and_view section.


3. incorrect

Something inside the current click_and_view section is incorrect.

Examples:

- an error message appeared
- an incorrect value was entered
- a required question was answered incorrectly
- the section cannot be completed because one of its existing
  answers must be corrected


IMPORTANT:

ONLY review the section created or controlled by:

{current_question}

Do NOT use unrelated questions elsewhere on the application when
determining the status.

For example:

If the original action was:

"Add More Work Experience"

and Company, Position, Start Date, and End Date appeared,

only judge those fields and the controls belonging to that work
experience section.

If an unrelated required question such as "Are you a veteran?"
exists elsewhere on the page, IGNORE IT.


CURRENT ANSWER:

{current_answer}


USER PROFILE:

First name: {state["first_name"]}
Last name: {state["last_name"]}
Email: {state["email"]}
Phone: {state["phone_number"]}

Address:
{state["address_line1"]}
{state["address_line2"]}
{state["city"]}
{state["user_state"]}
{state["zip_code"]}
{state["country"]}

Work authorized:
{state["work_authorized"]}

Work Experience: {state["work_experience"]}
Education: {state["education"]}

Requires sponsorship:
{state["requires_sponsorship"]}

Veteran:
{state["veteran"]}

Disability:
{state["disability"]}

LinkedIn:
{state["linkedin_url"]}

GitHub:
{state["github_url"]}

Portfolio:
{state["portfolio_url"]}

Resume:
{state["resume_text"]}

Cover Letter:
{state["cover_letter_text"]}


EXAMPLE 1:

{{
    click_and_view_status: complete,
    reason: The Add More Work Experience section has been completely
    filled out and saved.
}}


EXAMPLE 2:

{{
    click_and_view_status: more_questions,
    reason: The work experience section still has a required End Date
    question that has not been answered.
}}


EXAMPLE 3:

{{
    click_and_view_status: incorrect,
    reason: The Company field inside the newly added work experience
    contains an incorrect value and an error is displayed.
}}
"""

    response = review_click_and_view_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{old_bytes}"
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_bytes}"
                    }
                }
            ]
        }
    ])

    details = response["raw"]
    new_tokens = details.usage_metadata

    state = ai_token_tracker(
        new_tokens=new_tokens,
        state=state
    )

    decision = response["parsed"]

    print(f"Click and view review: {decision}")

    click_and_view_status = decision["click_and_view_status"]

    return click_and_view_status, state

def signup_process(state: ApplicationState):
    state = answser_question_process(state=state)
    return state
    
"""def signup_process(state: ApplicationState):
    old_bytes, ai_answers, boxes_details, state = answer_question_process(state=state)
    old_bytes, ai_answers, state = execute_question_process(old_bytes=old_bytes, ai_answers=ai_answers, boxes_details=boxes_details, state=state)
    ai_review, boxes_details, state = review_question_process(old_bytes=old_bytes, ai_answers=ai_answers, state=state)
    state = review_and_execute(ai_review=ai_review, boxes_details=boxes_details, state=state)
    return state"""

def load_test_user(state: ApplicationState):
    state["user_id"] = "12345"

    state["first_name"] = "Peyton"
    state["last_name"] = "Rivers"

    state["email"] = "peytonrivers716@gmail.com"
    state["password"] = "Bprivers1!"
    state["phone_number"] = "9197026557"
    state["preferred_name"] = "None"

    state["zip_code"] = "27596"

    state["address_line1"] = "90 Holstein Ln"
    state["address_line2"] = ""
    state["city"] = "Charlotte"
    state["user_state"] = "North Carolina"
    state["country"] = "United States"

    state["work_authorized"] = True
    state["requires_sponsorship"] = False
    state["veteran"] = False
    state["disability"] = False

    state["linkedin_url"] = "https://linkedin.com/in/johndoe"
    state["github_url"] = "https://github.com/johndoe"
    state["portfolio_url"] = "https://johndoe.dev"
    state["date"] = "August 8th 2025"
    state["work_experience"] = [{"company": "google", "position": "software engineer intern", "start_date": "May 6th 2026", "end_date": "August 8th 2026"}]
    state["education"] = [{"school": "UNC Charlotte", "major": "computer science", "start_date": "August 16 2025", "end_date": "May 5th 2029"}]


    state["resume_text"] = """
Peyton Rivers
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

"""with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    print(page.title)
    time.sleep(3)
    screenshot = page.screenshot()
    encoded_bytes = base64.b64encode(screenshot).decode("utf-8")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process",json=data)
    response_data = response.json()
    encoded_bytes = response_data["encoded_bytes"]
    decoded_new_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer_bytes = io.BytesIO(decoded_new_bytes)
    new_image = Image.open(buffer_bytes)
    new_image.show()
    print(response_data["boxes_details"])
    print(f"Ram memory: {memory.percent}%")"""


graph = StateGraph(ApplicationState)

graph.add_node("decide_page", decide_page)
graph.add_node("cookies_process", cookies_process)
graph.add_node("decide_routing", decide_routing)
graph.add_node("apply_process", apply_process)
graph.add_node("signup_process", signup_process)
graph.add_node("wait_process", wait_process)
graph.add_node("load_test_user", load_test_user)

graph.add_edge(START, "load_test_user")
graph.add_edge("load_test_user", "decide_page")
graph.add_conditional_edges("decide_page", decide_routing, {"cookies": "cookies_process", "apply": "apply_process", "signup": "signup_process", "forms": "signup_process", "wait": "wait_process", "exit": END})
graph.add_edge("cookies_process", "decide_page")
graph.add_edge("apply_process", "decide_page")
graph.add_edge("signup_process", "decide_page")
graph.add_edge("wait_process", "decide_page")

mapping = graph.compile()

def complete_application(url2: str):
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        current_page = {
            "page": page,
            "url": url,
        }
        page.goto(url)
        token_usage = {
            "tracker": 0,
            "input_tokens": 0,
            "cached_tokens": 0,
            "output_tokens": 0,
            "total_cost": 0
        }
        mapping.invoke({"url": url2, "current_page": current_page, "token_usage": token_usage})

complete_application(url)

print("hello")