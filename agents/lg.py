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
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess, AITokens, QuestionProcess, AnswerItem
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

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
question_process_llm = llm2.with_structured_output(QuestionProcess, include_raw=True)

url = "https://www.allstate.jobs/job/23556274/ai-software-engineer/"
print(url.title)

input_cost = 0.20 / 1000000
output_cost = 1.20 / 1000000
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
    page.wait_for_load_state("domcontentloaded")
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
    return encoded_bytes, boxes_details


def decide_page(state: ApplicationState):
    encoded_bytes = screenshot_process(state)
    prompt = """Your an AI Application Helper and your job is to decide what page this is
    1. cookies - You always choose this page if there are cookies on the page
    2. apply - You choose this page if we need to click apply now, apply manually, or we only need to click one buttton to continue
    3. signup - You choose this page if we need to signup or login or create an account for the user.
    4. forms - You choose this page if there is forms that need to be filled
    5. verification - You choose this page if there is a verification code that needs to be filled out, or if you need to verify an email, anything to do with verifying an account.
    6. error - You choose this page if there is an error or the page doesn't exist.
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
    else:
        # Fallback for "error" or any unexpected value
        return "end" 

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

follow_through_index: <integer icon number>
follow_through_reason: <brief explanation>

Example:

follow_through_index: 37
follow_through_reason: Icon 37 says "Accept All Cookies" and is located inside the cookie consent popup.
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
    print(f"Cookies new tokens: {new_tokens}")
    state = ai_token_tracker(new_tokens, state)
    decision = ai_response["parsed"]
    icon = decision["icon"]
    icon_reason = decision["icon_reason"]
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
    print(f"apply process: {boxes_details}")
    print(f"Apply process checkpoint 2")
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
reason: <brief explanation>

Example:

icon: 17
reason: The button says "Apply Manually," which is the preferred way to begin the application.

If there is no clear application button, return:
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
    icon = decision["icon"]
    print(icon)
    icon_reason = decision["icon_reason"]
    print(icon_reason)
    state = apply_action(icon=icon, boxes_details=boxes_details, state=state)
    print(f"Apply process checkpoint 4")
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

def find_question_process(state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details = omniparser_process(state)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    img = Image.open(buffer)
    img.show()
    time.sleep(10)
    prompt = f"""
Your an AI Applicant Helper that is apart of an assembly line to help answer fill out the user's information on the page.
You have an extremely inmportant task in looking at the page and the boxes details in order to find all the questions and it's options as well as with the information describing it.
There is no set format in how the responses need to be except that it will be a list of dictionaries and that each dictionary must contain an icon whether it's from the boxes details or custom.
Make Sure to take your time with the output!!!

Assembly line
1. Find Questions
2. Answer Questions
3. Execute
4. Review

boxes details: {boxes_details}

Inside the output you will give details of the objective that you have as well as details that go into every single question and their output.

Ex:
[
{{
"question": "What is your email"
"type": "text",,
"option": "",
"text_icon": 4
"input_icon": 28
}},
{{
"question": "Will you verify your that you consent to this form and all it's questions",
"type": "checkbox"
"options": [{{input_icon: 4, type: checkbox, text: yes}}, {{input_icon: 5, type: checkbox, text: no}}]
}},
{{
"question": "Will you verify your that you consent to this form and all it's questions",
"type": "checkbox"
"options": [{{input_icon: 4, type: checkbox, text: yes}}, {{icon: custom, type: checkbox, text: no, coordinates: [0.2325, 0.385, 0.485, .0585]}}]
}},
{{
"question": None,
"text": Save and Continue
"type": button,
"info": this is the submit buttom
"input_icon": 28
"text_icon": None
}}
]

"""
    response = question_process_llm.invoke([{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}

        ]
    }])
    details = response["raw"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens, state)
    decision = response["parsed"]
    ai_questions = decision["items"]
    print(f"Find question process questions: {ai_questions}")
    return ai_questions, encoded_bytes, boxes_details, state

def answer_question_process(state: ApplicationState):
    encoded_bytes, boxes_details = omniparser_process(state=state)
    prompt = f"""
Your an AI Signup Helper that is apart of an assembly line to help answer fill out the user's information on the page.
You have an extremely inmportant task in where you are going to look at the image input and  will be answering and how the questions.
You are filling out this based on the user's information and remember this is just a job application that you need to fill out for the user.

If there is a question that you skipped also let us know why

Ex:
{{
icon: 28,
action: "click"
reason: The Question is action me to confirm we approve of what's going on
}},
{{
icon: 17,
action: "fill",
action_text: "peytonrivers71@gmail.com"
reason: It asked to enter the user's email
}},
{{
icon: 30,
action: "skip"
reason: It was not relevant in filling out the user's application
}}

USER PROFILE


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


Employment eligibility:
- Authorized to work in the United States: {state["work_authorized"]}
- Requires current or future employment sponsorship: {state["requires_sponsorship"]}


Voluntary self-identification:
- Veteran: {state["veteran"]}
- Disability: {state["disability"]}


Professional links:
- LinkedIn: {state["linkedin_url"]}
- GitHub: {state["github_url"]}
- Portfolio: {state["portfolio_url"]}


Uploaded files:
- Resume file: {state["resume_upload"]}
- Cover-letter file: {state["cover_letter_upload"]}


Resume:
{state["resume_text"]}


Cover letter:
{state["cover_letter_text"]}
"""

    response = question_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])

    old_bytes = encoded_bytes
    details = response["raw"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    decision = response["parsed"]
    ai_answers = decision["items"]
    print(f"AI Answers: {ai_answers}")
    return old_bytes, ai_answers, boxes_details, state

def execute_question_process(old_bytes: str, ai_answers: list[dict], boxes_details: list[dict], state: ApplicationState):
    page = state["current_page"]["page"]
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    for i in range(len(ai_answers)):
        current_answer = ai_answers[i]
        action = current_answer["action"]
        if action == "skip":
            continue
        icon = current_answer["icon"]
        current_box = boxes_details[icon]
        coordinates = current_box["bbox"]
        page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
        if action == "click":
            page.mouse.click(page_x, page_y)
        if action == "fill":
            action_text = current_answer["action_text"]
            page.mouse.click(page_x, page_y)
            page.keyboard.type(action_text)
    encoded_bytes = screenshot_process(state=state)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    img = Image.open(buffer)
    img.show()
    time.sleep(20)
    return old_bytes, ai_answers, state

def review_question_process(old_bytes: str, ai_answers: list[dict], state: ApplicationState):
    encoded_bytes, boxes_details = omniparser_process(state=state)
    prompt = f"""
Your An AI Applicant Reviewer.
Your Job is to look at the answered questions and the new image and to determine if this is a new page or that we are in the same page and need to take the next action.
Guidelines:
- You will be returning two different types of output.
- Your first input will always show the page status whether it is 'complete' or 'incomplete' and this will be determined by looking at the two image inputs to see if they are the same page or a new page.
- The reason needs to be in the 2-3 sentence range and tell us what actions you are going to do and why the page is complete or incomplete
- If an answered question is correct you do not need tell us to revise that question.
- Action options: ["click", "delete", "delete and fill", "fill"]

The First image is the Old one,
The Second image is the new one which will be used if this page is incompletes.

You will be also showing what questions need to be edited or answers as well if we need to click the submit/continue button, always have the submit/continue button as the last element. 
Use the pattern of AI Answers as help.

AI Answers: {ai_answers}

Ex 1:
{{
page_status: 'complete'
reason: ...
}}

Ex 2:
{{
page_status: 'incomplete'
reason: ...
}},
{{
icon: 28,
action: 'click',
reason: This box needed to be checked and it wasn't previously,
}},
{{
icon: 30,
action: 'delete and fill',
action_text: peytonrivers71@gmail.com,
reason: The email was typed wrong and I'm typing it in correctly,
}},
{{
icon: 44,
action: "click",
reason: This boxed was checked and didn't need to be checked,
}},
{{
icon: 50,
action: "click"
reason: This is the submit button for this form and needs to be done to go to the next page.
}}
"""
    response = question_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{old_bytes}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}},
            ]
        }
    ])
    details = response["raw"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    decision = response["parsed"]
    ai_review = decision["items"]
    print(f"AI review decision: {ai_review}")
    return ai_review, boxes_details, state

def review_and_execute(ai_review: list[dict], boxes_details: list[dict], state: ApplicationState):
    page = state["current_page"]["page"]
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    first_box = ai_review[0]
    page_status = first_box["page_status"]
    if page_status == "complete":
        return state
    for i in range(1, len(ai_review)):
        current_review = ai_review[i]
        icon = current_review.get("icon")
        current_box = boxes_details[icon]
        coordinates = current_box["bbox"]
        page_x, page_y = coordinates_process(coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
        action = current_review.get("action")
        action_text = current_review.get("action_text")
        action_process(action=action, page_x=page_x, page_y=page_y, state=state, action_text=action_text)
    screenshot = page.screenshot()
    buffer = io.BytesIO(screenshot)
    img = Image.open(buffer)
    img.show()
    time.sleep(20)
    return state

def action_process(action, page_x, page_y, state: ApplicationState, action_text=None):
    page = state["current_page"]["page"]
    if action == "click":
        page.mouse.click(page_x, page_y)
    if action == "fill":
        page.mouse.click(page_x, page_y)
        page.keyboard.type(action_text)
    if action == "delete and fill":
        page.mouse.click(page_x, page_y)
        page.keyboard.press("ControlOrMeta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(action_text)
    if action == "delete":
        page.mouse.click(page_x, page_y)
        page.keyboard.press("ControlOrMeta+A")
        page.keyboard.press("Backspage")
    
def signup_process(state: ApplicationState):
    old_bytes, ai_answers, boxes_details, state = answer_question_process(state=state)
    old_bytes, ai_answers, state = execute_question_process(old_bytes=old_bytes, ai_answers=ai_answers, boxes_details=boxes_details, state=state)
    ai_review, boxes_details, state = review_question_process(old_bytes=old_bytes, ai_answers=ai_answers, state=state)
    state = review_and_execute(ai_review=ai_review, boxes_details=boxes_details, state=state)
    return state

def load_test_user(state: ApplicationState):
    state["user_id"] = "12345"

    state["first_name"] = "John"
    state["last_name"] = "Doe"
    state["preferred_name"] = "John"

    state["email"] = "peytonrivers71@gmail.com"
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
graph.add_node("load_test_user", load_test_user)

graph.add_edge(START, "load_test_user")
graph.add_edge("load_test_user", "decide_page")
graph.add_conditional_edges("decide_page", decide_routing, {"cookies": "cookies_process", "apply": "apply_process", "signup": "signup_process", "forms": "signup_process","end": END})
graph.add_edge("cookies_process", "decide_page")
graph.add_edge("apply_process", "decide_page")
graph.add_edge("signup_process", "decide_page")

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