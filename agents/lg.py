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
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess, AITokens, QuestionProcess, AnswerItem, MarkdownProcess
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

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
url = "https://jobs.fidelity.com/en/jobs/2132114/leap-software-engineer/"
url = "https://www.allstate.jobs/job/23538686/software-engineer-all-levels-/"
url = "https://cloudfront.careeronestop.org/JusticeImpacted/Toolkit/practice-job-application-form.aspx?practice-job-application-form.aspx="
# url = "https://demoqa.com/select-menu"
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
    return encoded_bytes, boxes_details


def decide_page(state: ApplicationState):
    encoded_bytes = screenshot_process(state)
    prompt = """Your an AI Application Helper and your job is to decide what page this is
    1. cookies - You always choose this page if there are cookies on the page
    2. apply - You choose this page if we need to click apply now, apply manually, or we only need to click one buttton to continue
    3. forms - You choose this page if there is forms that need to be filled
    4. verification - You choose this page if there is a verification code that needs to be filled out, or if you need to verify an email, anything to do with verifying an account.
    5. exit - You choose this page if there the url isn't active or we have finished the job application.
    6. wait - if the page hasn't loaded you choose this process.

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
    else:
        # Fallback for "error" or any unexpected value
        return "end" 

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
    response = question_process_llm2.invoke([{
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

You will answer every question with 1 of these 10 actions.

Immediate Action Section

1. skip - when you want to skip a question

2. fill - when you want to fill out a question

3. fill_with_time - used when you want to fill out an element that requires a time value

4. delete - used when you want to delete the given text

5. delete_and_fill - used when you want to delete the given text and then fill it out with new information

6. click - when you want to click or unclick an element


Process Action Section

7. upload_resume - Used when the current question requires the user's resume file to be uploaded.

8. upload_cover_letter - Used when the current question requires the user's cover letter file to be uploaded.

9. click_and_view - Used when clicking an element will reveal or load additional information, questions, fields, or a new section that must be analyzed before continuing.

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
    action_text: johndoe@gmail.com,
    icon: 28,
    reason: This question asks for the user's email address, so the email input should be filled.
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
    reason: This input contains incorrect information and should be cleared.
}}

Ex 5:
{{
    action: delete_and_fill,
    action_text: John,
    icon: 42,
    reason: The current first name is incorrect, so the existing value should be deleted and replaced with John.
}}

Ex 6:
{{
    action: click,
    icon: 32,
    reason: This question asks whether the user is a U.S. citizen and Yes is the correct option, so this element should be clicked.
}}

Ex 7:
{{
    action: upload_resume,
    icon: 50,
    reason: This question requires the user's resume to be uploaded.
}}

Ex 8:
{{
    action: upload_cover_letter,
    icon: 52,
    reason: This question requires the user's cover letter to be uploaded.
}}

Ex 9:
{{
    action: click_and_view,
    icon: 22,
    question: Add More Work Experience,
    reason: The user has additional work experience that needs to be entered. Clicking this element will reveal additional fields that must be analyzed before continuing.
}}

Ex 10:
{{
    action: markdown,
    icon: 60,
    question: What U.S. State are you in?,
    reason: This question uses a dropdown with multiple selectable state options. The markdown process should open the element, discover the available options, and determine which option matches the user's information.
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

Voluntary self-identification:
- Veteran: {state["veteran"]}
- Disability: {state["disability"]}

Professional links:
- LinkedIn: {state["linkedin_url"]}
- GitHub: {state["github_url"]}
- Portfolio: {state["portfolio_url"]}


Resume: {state["resume_text"]}
Cover letter: {state["cover_letter_text"]}
"""

    new_prompt = f"""
You're an AI Applicant Helper who is currently in the forms process.

You're job is to look at the current forms page and to have these responsibilities.
1. Answer Every Required Question
2. Look at any error's on the page and do your best to handle them
3. Answer every question by using two things: the user's profile and common sense
4. Make sure to use common sense while filling out this form

You will answer every question with 1 of these 10 actions.

Immediate Action Section

1. skip - when you want to skip a question

2. fill - when you want to fill out a question

3. fill_with_time - used when you want to fill out an element that requires a time or date value.

4. delete - used when you want to delete the given text

5. delete_and_fill - used when you want to delete the given text and then fill it out with new information

6. click - when you want to click or unclick an element


Process Action Section

7. upload_resume - Used when the current question requires the user's resume file to be uploaded.

8. upload_cover_letter - Used when the current question requires the user's cover letter file to be uploaded.

9. click_and_view - Used when clicking an element will reveal or load additional information, questions, fields, or a new section that must be analyzed before continuing.

10. markdown - Used when clicking an element opens a list of selectable options, such as a dropdown, combobox, menu, or similar selection component. The markdown process is responsible for opening the element, discovering the available options, and selecting the correct option.

11. submit - Used for buttons that finalize the current page or section, such as Submit, Save and Continue, Continue, Next, or similar progression buttons.


Look at the boxes details and the image to help you determine which icon we are looking at.

boxes_details: {boxes_details}

Within the icon's you pick, pick the icon that chooses the option and not the question if possible.

Markdown answers must have a custom 'background_point' that will be used to click the background of page. This background point should be in list format, this list format should include the percent of the page. [0.5, 0.5] would represent 50% of the x-axis and 50% of the yaxis. [0.39, 0.48] 0.39 would represent 39% of the x-axis and 0.48 would represent 48% of the y-axis.

You must follow the markdown Example format!!!

Ex 1:
{{
    action: skip,
    reason: This question has already been filled out correctly and does not require any action.
}}

Ex 2:
{{
    action: fill,
    action_text: johndoe@gmail.com,
    icon: 28,
    reason: This question asks for the user's email address, so the email input should be filled.
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
    reason: This input contains incorrect information and should be cleared.
}}

Ex 5:
{{
    action: delete_and_fill,
    action_text: John,
    icon: 42,
    reason: The current first name is incorrect, so the existing value should be deleted and replaced with John.
}}

Ex 6:
{{
    action: click,
    icon: 32,
    reason: This question asks whether the user is a U.S. citizen and Yes is the correct option, so this element should be clicked.
}}

Ex 7:
{{
    action: upload_resume,
    icon: 50,
    reason: This question requires the user's resume to be uploaded.
}}

Ex 8:
{{
    action: upload_cover_letter,
    icon: 52,
    reason: This question requires the user's cover letter to be uploaded.
}}

Ex 9:
{{
    action: click_and_view,
    icon: 22,
    question: Add More Work Experience,
    reason: The user has additional work experience that needs to be entered. Clicking this element will reveal additional fields that must be analyzed before continuing.
}}

Ex 10:
{{
    action: markdown,
    icon: 60,
    current_question: What U.S. State are you in?,
    reason: This question uses a dropdown with multiple selectable state options. The markdown process should open the element, discover the available options, and determine which option matches the user's information.
    background_point: [0.38, 0.92]
    bacground_reason: This point is completely the background with no text or clickable item.
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

Voluntary self-identification:
- Veteran: {state["veteran"]}
- Disability: {state["disability"]}

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
        execute_action(current_answer=current_answer, current_box=current_box, state=state)
    return state

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
    if action == "fill_with_time":
        action_text = current_answer.get("action_text")
        if not action_text:
            return state
        page.mouse.click(page_x, page_y)
        page.keyboard.press("ArrowLeft")
        time.sleep(1)
        page.keyboard.press("ArrowLeft")
        time.sleep(1)
        page.keyboard.type(action_text)
    if action == "click":
        page.mouse.click(page_x, page_y)
        time.sleep(2)
    if action == "markdown":
        page.mouse.click(page_x, page_y)
        body_text = page.locator("body").inner_text()
        page.keyboard.press("ArrowDown")
        markdown_process(current_answer=current_answer, page_x=page_x, page_y=page_y, body_text=body_text, state=state)
    if action == "submit":
        encoded_bytes = screenshot_process(state=state)
        decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
        buffer = io.BytesIO(decoded_bytes)
        image = Image.open(buffer)
        image.show()
        time.sleep(10)
        page.mouse.click(page_x, page_y)

def markdown_process(current_answer: dict, page_x: float, page_y: float, body_text: str, state: ApplicationState):
    page = state["current_page"]["page"]
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    encoded_bytes = screenshot_process(state=state)
    current_question = current_answer.get("current_question")
    background_point = current_answer.get("background_point")
    background_x = full_page_width * background_point[0]
    background_y = full_page_height * background_point[1]
    prompt = f"""
You're an AI Applicant Helper that is in the markup process.

Markup definition: markdown - Used when clicking an element opens a list of selectable options, such as a dropdown, combobox, menu, or similar selection component. The markdown process is responsible for opening the element, discovering the available options, and selecting the correct option.

You're goal is to look at the the body text + the image to find all the options for the question we are in.

current_question: {current_question}
body_text: {body_text}

You will showcase all the options with the text and the option number in order.
You will showcase the option choice you hope to click.
You will also showcase the current option that our keyboard is at, so we know how many times we need to use the keyboard to go up or down to click the option_choice.
Use the user info and common sense to help answer the markup.

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

Voluntary self-identification:
- Veteran: {state["veteran"]}
- Disability: {state["disability"]}

Professional links:
- LinkedIn: {state["linkedin_url"]}
- GitHub: {state["github_url"]}
- Portfolio: {state["portfolio_url"]}


Resume: {state["resume_text"]}
Cover letter: {state["cover_letter_text"]}
---------------

Example output
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
------------------
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
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    decision = response["parsed"]
    print(f"Markdown decision: {decision}")
    options = decision["options"]
    option_choice = decision["option_choice"]
    current_option = decision["current_option"]
    arrow_count = option_choice - current_option
    page.mouse.click(background_x, background_y)
    page.mouse.click(page_x, page_y)
    page.keyboard.press("ArrowDown")
    print(f"How many times we need to move the arrow: {arrow_count}")
    if arrow_count == 0:
        page.keyboard.press("Enter")
    if arrow_count < 0:
        for i in range(abs(arrow_count)):
            page.keyboard.press("ArrowUp")
        page.keyboard.press("Enter")
    if arrow_count > 0:
        for i in range(arrow_count):
            page.keyboard.press("ArrowDown")
            print(f"Arrow down: {i+1}")
            time.sleep(1)
        page.keyboard.press("Enter")
    encoded_bytes = screenshot_process(state=state)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image.show()
    time.sleep(10)
    time.sleep(5)

def signup_process(state: ApplicationState):
    state = answser_question_process(state=state)
    
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
    state["preferred_name"] = "John"

    state["email"] = "peytonrivers716@gmail.com"
    state["password"] = "Bprivers1!"
    state["phone_number"] = "9197026557"

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
