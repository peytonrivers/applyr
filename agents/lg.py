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
from agents.state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess, AITokens, QuestionProcess, AnswerItem, MarkdownProcess, ReviewMarkdownProcess, ReviewClickAndViewProcess, FindIcon, ReviewQuestionProcess
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests
import cv2
import math
import subprocess
from database.storage import supabase

import pyautogui
pyautogui.FAILSAFE = False

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
meta_key = os.getenv("META_KEY")

META_MODEL = "Qwen/Qwen3-VL-30B-A3B-Instruct"

MODEL_NAME = "gpt-5.4-nano"
MODEL_NAME2 = "gpt-5.6-luna"

llm = ChatOpenAI(model=MODEL_NAME, temperature=0.3, api_key=openai_key)
llm2 = ChatOpenAI(model=MODEL_NAME2, temperature=0.1, reasoning_effort="high", api_key=openai_key)
llm3 = ChatOpenAI(model=MODEL_NAME2, temperature=0.1, api_key=openai_key)

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
review_question_process_llm3 = llm3.with_structured_output(ReviewQuestionProcess, include_raw=True)
markdown_process_llm2 = llm2.with_structured_output(MarkdownProcess, include_raw=True)
review_markdown_process_llm3 = llm3.with_structured_output(ReviewMarkdownProcess, include_raw=True)
review_click_and_view_process_llm3 = llm3.with_structured_output(ReviewClickAndViewProcess, include_raw=True)
find_icon_process_llm3 = llm3.with_structured_output(FindIcon, include_raw=True)
url = "https://jobs.fidelity.com/en/jobs/2132114/leap-software-engineer/"
url = "https://www.allstate.jobs/job/23527822/senior-product-engineer-software-java-/"
# url = "https://www.allstate.jobs/job/23283268/-net-senior-software-engineer/"
url = "https://www.allstate.jobs/job/23473343/cloud-services-lead-software-engineer/"
url = "https://www.allstate.jobs/job/23613565/java-development-lead-systems-engineer/"
url = "https://cloudfront.careeronestop.org/JusticeImpacted/Toolkit/practice-job-application-form.aspx?practice-job-application-form.aspx="
url = "https://www.allstate.jobs/job/23660063/senior-consultant-ii-ai-ml-engineer/"
print(url.title)
input_cost = 0.20 / 1000000
output_cost = 1.25 / 1000000
cached_cost = 0.02 / 1000000
model_ratios = [["gpt-5.4-nano", 0.20 / 1000000, 1.25 / 1000000, 0.02 / 1000000], ["gpt-5.6-luna", 0.20 / 1000000, 1.20 / 1000000, 0.02 / 1000000]]


def ai_token_tracker(new_tokens: dict, model_name: str, state: ApplicationState):
    token_check = False
    for i in range(len(model_ratios)):
        current_model = model_ratios[i]
        current_model_name = current_model[0]
        if model_name == current_model_name:
            input_cost = current_model[1]
            output_cost = current_model[2]
            cached_cost = current_model[3]
            token_check = True
            break
    token_usage = state["token_usage"]
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

def details_process(details: dict):
    new_tokens = details.usage_metadata
    response_metadata = details.response_metadata
    total_model_name = response_metadata["model_name"]
    print(f"total model: {total_model_name}")
    model_name = ""
    dash_count = 0
    for i in range(len(total_model_name)):
        letter = total_model_name[i]
        if letter == "-":
            dash_count += 1
        if dash_count == 3:
            break
        model_name += letter
    print(f"model: {model_name}")
    return new_tokens, model_name  

def empty_pixel_process(encoded_bytes: str, coordinates: list[list], full_page_width: int, full_page_height: int):
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    format = image.format
    if format != "PNG":
        image.save("my_screenshot.png")
    image_width, image_height = image.size
    np_image = np.array(image)
    cv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    black = (0, 0, 0)
    for i in range(len(coordinates)):
        coordinate = coordinates[i]
        x1 = round(coordinate[0] * image_width)
        y1 = round(coordinate[1] * image_height)
        x2 = round(coordinate[2] * image_width)
        y2 = round(coordinate[3] * image_height)
        height_diff = y2 - y1
        for l in range(height_diff):
            cv_image = cv2.line(cv_image, (x1, y1), (x2, y1), black, 3)
            y1 += 1
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    _, cv_image = cv2.threshold(cv_image, 127, 255, cv2.THRESH_BINARY)
    image_height, image_width = cv_image.shape

    mod_width = image_width % 5
    mod_height = image_height % 5

    new_width = image_width - mod_width
    new_height = image_height - mod_height

    width_divider = int(new_width / 5)
    height_divider = int(new_height / 5)

    width_index = [new_width]
    height_index = [new_height]
    for size in range(4):
        new_height -= height_divider
        new_width -= width_divider
        height_index.insert(0, new_height)
        width_index.insert(0, new_width)

    perfect_section = width_divider * height_divider

    section_coordinates = []

    for p in range(len(height_index)):
        current_height = height_index[p]
        for o in range(len(width_index)):
            current_width = width_index[o]
            section_coordinates.append([current_height - height_divider,current_width - width_divider,current_height, current_width])
    white_section_tracker = []

    for i in range(len(height_index)):
        current_height = height_index[i]
        if i == 0:
            prior_height = 0
        else:
            prior_height = height_index[i-1]
        for l in range(len(width_index)):
            white_pixel_tracker = 0
            current_width = width_index[l]
            if l == 0:
                prior_width = 0
            else:
                prior_width = width_index[l-1]
            for j in range(prior_height, current_height):
                for m in range(prior_width, current_width):
                    current_pixel = cv_image[j, m]
                    if current_pixel == 255:
                        white_pixel_tracker += 1
            white_section_tracker.append(white_pixel_tracker)
    max_section = white_section_tracker[0]
    max_index = 0
    for n in range(len(white_section_tracker)):
        current_section = white_section_tracker[n]
        if current_section > max_section:
            max_section = current_section
            max_index = n
    max_section_coordinates = section_coordinates[max_index]
    y1, x1, y2, x2 = max_section_coordinates

    cropped_x = (x1 + x2) / 2
    cropped_y = (y1 + y2) / 2
    white_x = (full_page_width / image_width ) * cropped_x
    white_y = (full_page_height / image_height) * cropped_y
    return white_x, white_y


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

def page_width_and_height_process(state: ApplicationState):
    page = state["current_page"]["page"]
    for i in range(500, 1301, 100):
        page.set_viewport_size({"width": i, "height": 500})
        real_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if real_height < 5000:
            page.set_viewport_size({"width": i, "height": real_height})
            print(f"image width: {i}")
            print(f"image height: {real_height}")
            return i, real_height
    real_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight )}""")
    print(f"image width: {i}")
    print(f"image height: {real_height}")
    return 1300, real_height

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
    full_page_width, full_page_height = page_width_and_height_process(state=state)
    screenshot = page.screenshot()
    encoded_bytes = base64.b64encode(screenshot).decode("utf-8")
    return encoded_bytes, full_page_width, full_page_height

def omniparser_process(state: ApplicationState):
    page = state["current_page"]["page"]
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    print(f"full page height before omniparser: {full_page_height}")
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state)
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    response_data = response.json()
    encoded_bytes = response_data["encoded_bytes"]
    boxes_details = response_data["boxes_details"]
    coordinates = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        coordinate = current_box["bbox"]
        coordinates.append(coordinate)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    return encoded_bytes, boxes_details, full_page_width, full_page_height

def boxes_only_process(encoded_bytes: str, boxes_details: list[dict]):
    coordinates = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        coordinates.append(current_box["bbox"])
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    width, height = image.size
    arr = np.array(image)
    column_remove = list(range(width))
    row_remove = list(range(height))
    for l in range(len(coordinates)):
        box = coordinates[l]
        x1, y1 = (round(box[0] * width), round(box[1] * height))
        x2, y2 = (round(box[2] * width), round(box[3] * height))
        temp_column = list(range(x1-2, x2+2))
        temp_row = list(range(y1-10, y2+10))
        for column in temp_column:
            if column in column_remove:
                column_remove.remove(column)
        for row in temp_row:
            if row in row_remove:
                row_remove.remove(row)
    arr = np.delete(arr, column_remove, axis=1)
    arr = np.delete(arr, row_remove, axis=0)
    new_image = Image.fromarray(arr)
    new_image_buffer = io.BytesIO()
    new_image.save(new_image_buffer, format="PNG")
    new_image_bytes = new_image_buffer.getvalue()
    encoded_bytes = base64.b64encode(new_image_bytes).decode("utf-8")
    return encoded_bytes


def decide_page(state: ApplicationState):
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    token_usage = state.get("token_usage")
    prompt = f"""Your an AI Application Helper and your job is to decide what page this is
    1. cookies - You always choose this page if there are cookies on the page
    2. apply - You choose this page if we need to click apply now, apply manually, or we only need to click one buttton to continue
    3. forms - You choose this page if there is forms that need to be filled
    4. verification - You choose this page if there is a verification code that needs to be filled out, or if you need to verify an email, anything to do with verifying an account.
    5. exit - You choose this page if there the url isn't active or we have finished the job application or if they cost is great than $0.005.
    6. wait - if the page is blank and has nothing forms, steps, or content on the page then choose the wait process. 

    Current Cost: ${state["token_usage"]["total_cost"]}

    IF ${state["token_usage"]["total_cost"]} > $0.10, choose exit!!!
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
    print(f"decide page: {response}")
    details = response["raw"]
    print(f"details: {details}")
    decision = response["parsed"]
    new_tokens, model_name = details_process(details=details)
    action = decision["action"]
    action_reason = decision["action_reason"]
    if action == "exit":
        state["leaving_reason"] = action_reason
    state["action"] = action

    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        state["action"] = "exit"
        state["leaving_reason"] = f"The cost extended above $0.10 at the decide page process with the total being ${total_cost}"

    print(f"AI Tokens: {new_tokens}")
    print(f"AI details: {details}")
    print(f"AI decision: {decision}")
    print(f"decide page memory pecent: {memory.percent}%")
    return state

def decide_routing(state: ApplicationState):
    action = state["action"]
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        print("it came from routing")
        state["leaving_reason"] = "total cost greater than $0.10"
        return "exit"
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

def signup_routing(state: ApplicationState):
    signup_action = state.get("signup_action")
    if signup_action == "max_tries":
        return "max_tries"
    elif signup_action == "different_page":
        return "different_page"
    elif signup_action == "new_form":
        return "new_form"
    else:
        return "decide_page"

def wait_process(state: ApplicationState):
    page = state.get("page")
    if not page:
        state["leaving_reason"] = "page not found"
        return "exit"
    page = page.get("current_page")
    if not page:
        state["leaving_reason"] = "page not found"
        return "exit"
    time.sleep(20)
    body_text = page.locator("body").inner_text()
    if len(body_text) > 20:
        state["wait_action"] = "continue"
        return "continue"
    time.sleep(20)
    body_text = page.locator("body").inner_text()
    if len(body_text) > 20:
        state["wait_action"] = "continue"
        return "continue"
    time.sleep(20)
    body_text = page.locator("body").inner_text()
    if len(body_text) > 20:
        state["wait_action"] = "continue"
        return "continue"
    state["wait_action"] = "exit"
    state["leaving_reason"] = "The page would not load"
    return "exit"

def wait_routing(state: ApplicationState):
    wait_action = state.get("wait_action")
    if wait_action == "continue":
        return "continue"
    else:
        return "continue"
def cookies_process(state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    new_box = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        content = current_box["content"]
        new_box.append([icon, box_type, content])

    prompt = f"""
You are an AI Applicant Helper.

Your job is to examine the screenshot and the detected interface elements, then identify the single icon that accepts or confirms the website's cookie consent prompt.

You will receive:
1. A screenshot of the webpage.
2. Detected interface elements in `boxes_details`.

Use BOTH the screenshot and `Page Elements` to make your decision.

Page Elements Format:
[icon, type, content]

PAGE ELEMENTS
{new_box}

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

Example:

icon: 37

Example if no cookies are present:
icon: None
"""

    ai_response = cookies_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                ]}])
    details = ai_response["raw"]
    new_tokens, model_name = details_process(details=details)
    print(f"new tokens: {new_tokens}")
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        state["action"] = "exit"
        state["leaving_reason"] = f"The cost extended above $0.10 at the cookies page process with the total being ${total_cost}"
    decision = ai_response["parsed"]
    print(f"AI Decision: {decision}")
    icon = decision.get("icon")
    if not icon:
        return state
    cookies_action(icon=icon, boxes_details=boxes_details, full_page_width=full_page_width, full_page_height=full_page_height, state=state)
    print(f"cookies icon: {icon}")
    return state


def cookies_action(icon: int, boxes_details: json, full_page_width: int, full_page_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
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
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    new_box = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        content = current_box["content"]
        new_box.append([icon, box_type, content])
    prompt = f"""
You are an AI Applicant Helper.

Your goal is to start or continue the job application process.

You will receive:
1. A screenshot of the webpage.
2. The detected interface elements (`boxes_details`).

Use BOTH the screenshot and `boxes_details` to determine which icon should be clicked.

Page Elements Format:
[icon, type, content]

PAGE ELEMENTS
{new_box}

INSTRUCTIONS

- Find the single best icon that advances the user into the application.
- Always prefer applying directly on the employer's website.
- Always choose "apply manually" or something that you have to manually input your application.
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

Example:
icon: 17

Example for no application button found:
icon: None
"""
    response = apply_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                ]}])
    details = response["raw"]
    decision = response["parsed"]
    new_tokens, model_name = details_process(details=details)
    print(f"new tokens: {new_tokens}")
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        state["action"] = "exit"
        state["leaving_reason"] = f"The cost extended above $0.10 at the apply page process with the total being ${total_cost}"
    icon = decision.get("icon")
    if not icon:
        return state
    print(f"apply icon: {icon}")
    state = apply_action(icon=icon, boxes_details=boxes_details, full_page_width=full_page_width, full_page_height=full_page_height, state=state)
    return state
    
def apply_action(icon: int, boxes_details: json, full_page_width: int, full_page_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    clickable_item = boxes_details[icon]
    coordinates = clickable_item["bbox"]
    x1 = coordinates[0]
    y1 = coordinates[1]
    x2 = coordinates[2]
    y2 = coordinates[3]
    middle_x = (x1 + x2) / 2
    middle_y = (y1 + y2) / 2
    print(f"full page width: {full_page_width}")
    print(f"full page height: {full_page_height}")
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
    page = state["current_page"]["page"]
    all_boxes = []
    full_text = page.locator("body").inner_text()

    body_text = " ".join(full_text.split()[:100])
    all_text = [body_text]

    for attempt in range(5):
        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
        encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
        encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)
        decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
        buffer = io.BytesIO(decoded_bytes)
        image = Image.open(buffer)
        image.show()
        time.sleep(2)
        new_box = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            content = current_box["content"]
            new_box.append([icon, box_type, content])
        all_boxes.append(new_box)
        coordinates = []
        for coord in range(len(boxes_details)):
            current_box = boxes_details[coord]
            coordinate = current_box["bbox"]
            coordinates.append(coordinate)
        white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
        
        prompt = f"""
You are completing a job application form using the user's profile and the visible page.

GOAL
- Correctly answer every required question.
- Fix visible validation errors.
- Leave already-correct answers unchanged.
- Use the user's profile first and reasonable inference when necessary.
- Return an action for every relevant visible question.
- Use the input/option icon, not the question-label icon, when possible.

ACTIONS
skip: No change needed or question should be skipped.
fill: Fill an empty input. Requires action_text + icon.
fill_with_time: Fill a date/time input. Requires action_text + icon.
delete: Clear incorrect/unwanted text. Requires icon.
delete_and_fill: Replace existing text. Requires action_text + icon.
click: Select/unselect an immediately answerable option. Requires icon.
upload_resume: Resume upload field. Requires icon.
upload_cover_letter: Cover-letter upload field. Requires icon.
click_and_view: Click only when it reveals additional fields/questions that must be completed. Requires icon + question.
markdown: Dropdown/combobox/menu requiring option discovery and selection. Requires icon + current_question.
submit: Finalize or advance the completed page/section. Requires icon.

IMPORTANT
- Use click for visible choices such as radio buttons and checkboxes.
- Use markdown for dropdown/select-style controls.
- Use click_and_view only when clicking reveals additional information that must be handled.
- Submit only after required visible questions are correctly handled.
- Do not list any elements you skip.
- Use delete or delete and fill if one of the inputted answers is incorrect.

Page Elements format
[icon, type, content]

PAGE ELEMENTS
{new_box}

ITEMS ELEMENTS

skip: [action]

fill: [action, icon, action_text]

fill_with_time: [action, icon, action_text]

delete: [action, icon]

delete_and_fill: [action, icon, action_text]

click: [action, icon]

upload_resume: [action, icon]

upload_cover_letter: [action, icon]

click_and_view: [action, icon, current_question]

markdown: [action, icon, current_question]

submit: [action, icon, submit_text]

ACTIONS

Example:

items: [["skip"], ["fill", 28, {state["email"]}], ["fill_with_time", 35, "08/01/2020"], ["delete", 38], ["delete_and_fill", 42, {state["first_name"]}], ["click", 32], ["upload_resume", 50], ["upload_cover_letter", 52], ["click_and_view", 22, "Add More Work Experience"], ["markdown", 60, "What U.S. State are you in?"], ["submit", 30]]

USER PROFILE
Account:
email={state["email"]}
password={state["password"]}

Personal:
first_name={state["first_name"]}
last_name={state["last_name"]}
phone={state["phone_number"]}

Address:
address1={state["address_line1"]}
address2={state["address_line2"]}
city={state["city"]}
state={state["user_state"]}
zip={state["zip_code"]}
country={state["country"]}
date={state["date"]}

Eligibility:
work_authorized={state["work_authorized"]}
requires_sponsorship={state["requires_sponsorship"]}

Self-ID:
veteran={state["veteran"]}
disability={state["disability"]}

Professional:
linkedin={state["linkedin_url"]}
github={state["github_url"]}
portfolio={state["portfolio_url"]}

Work Experience:
{state["work_experience"]}

Education:
{state["education"]}

Resume:
{state["resume_text"]}

Cover Letter:
{state["cover_letter_text"]}

If asked how the job was found, prefer "Other", "Job Board", "Website", or the closest equivalent.
"""

        response = question_process_llm2.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes2}"}}
                ]
            }
        ])
        details = response["raw"]
        print(f"details: {details}")
        new_tokens, model_name = details_process(details=details)
        print(f"new tokens: {new_tokens}")
        state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
        total_cost = state["token_usage"]["total_cost"]
        if total_cost > 0.10:
            state["action"] = "exit"
            state["leaving_reason"] = f"The cost extended above $0.10 at the signup page process with the total being ${total_cost}"
        answers = response["parsed"]
        ai_answers = answers["items"]
        print(f"AI Answers: {ai_answers}")
        """submit_index = None
        click_and_view_elements = []
        click_and_view_index = 0
        state["click_and_view_index"] = click_and_view_index
        for i in range(len(ai_answers)):
            current_answer = ai_answers[i]
            action = current_answer[0]
            if action == "click_and_view":
                current_click = []
                current_click.append(current_answer)
                current_click_icon = current_answer[1] if len(current_answer) > 1 else None
                if not current_click_icon:
                    current_click.append({"icon_status": None})
                    click_and_view_elements.append(current_click)
                    continue
                coordinates = boxes_details[current_click_icon]["bbox"]
                page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
                page.mouse.click(page_x, page_y, button="right")
                current_click_element = page.evaluate(
                            () => {
                                const el = document.activeElement;
                                const box = el.getBoundingClientRect();
                
                                return {
                                    tag: el.tagName.toLowerCase(),
                
                                    attributes: Object.fromEntries(
                                        Array.from(el.attributes).map(attr => [
                                            attr.name,
                                            attr.value
                                        ])
                                    ),
                
                                    text: el.innerText,
                
                                    bounding_box: {
                                        x: box.x,
                                        y: box.y,
                                        width: box.width,
                                        height: box.height
                                    },
                
                                    center: {
                                        x: box.x + box.width / 2,
                                        y: box.y + box.height / 2
                                    }
                                };
                            }
                        )
                current_click_element["icon_status"] = True
                current_click.append(current_click_element)
                click_and_view_elements.append(current_click)
                page.mouse.click(white_x, white_y)
            
            if action == "submit":
                submit_index = i
                submit_icon = current_answer[1] if len(current_answer) > 1 else None
                if not submit_icon:
                    continue
                coordinates = boxes_details[submit_icon]["bbox"]
                page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
                page.mouse.click(page_x, page_y, button="right")
                submit_element = page.evaluate(
                            () => {
                                const el = document.activeElement;
                                const box = el.getBoundingClientRect();
                
                                return {
                                    tag: el.tagName.toLowerCase(),
                
                                    attributes: Object.fromEntries(
                                        Array.from(el.attributes).map(attr => [
                                            attr.name,
                                            attr.value
                                        ])
                                    ),
                
                                    text: el.innerText,
                
                                    bounding_box: {
                                        x: box.x,
                                        y: box.y,
                                        width: box.width,
                                        height: box.height
                                    },
                
                                    center: {
                                        x: box.x + box.width / 2,
                                        y: box.y + box.height / 2
                                    }
                                };
                            }
                        )
                state["submit_element"] = submit_element
                page.mouse.click(white_x, white_y)
        if submit_index == None:
            state["submit_element"] = None
        if len(click_and_view_elements) == 0:
            state["click_and_view_elements"] = []
        else:
            state["click_and_view_elements"] = click_and_view_elements
        print(f"Click and view elements in state answer question: {state.get("click_and_view_elements")}")"""
        state = action_process(ai_answers=ai_answers, boxes_details=boxes_details, state=state, full_page_width=full_page_width, full_page_height=full_page_height, white_x=white_x, white_y=white_y)
        state, decision = review_answer_question_process(state=state, all_text=all_text)
        if decision == "same_form":
            continue
        elif decision == "new_form":
            state["signup_action"] = "new_form"
            return state
        elif decision == "different_page":
            state["signup_action"] = "different_page"
            return state

    state["signup_action"] = "max_tries"
    state["leaving_reason"] = "Max tries for the forms process"
    return state

def review_answer_question_process(state: ApplicationState, all_text: list[str]):
    page = state["current_page"]["page"]
    total_cost = state["token_usage"]["total_cost"]
    if total_cost >= 0.10:
        state["leaving_reason"] = "Total cost greater than $0.10"
        return state, "total_cost"
    encoded_bytes = screenshot_process(state=state)
    full_text = page.locator("body").inner_text()

    body_text = " ".join(full_text.split()[:100])
    all_text.append(body_text)
    prompt = f"""
Your an AI Applicant helper and your job is to look at the two different lists of body text and determine.
1. same_form - all the body text look similar.
2. new_form - The old forms page is complete and we are on a new forms page with the body text looking different.
3. different_page - this is niether the old forms page and not a new forms page as well and is instead something different

All text:
{all_text}

Ex 1:
{{decision: same_form, reason: There is an error and the ai answers look similar to the current page}}

Ex 2:
{{decision: new_form, reason: This a new form page where it is different to the old forms questions}}

Ex 3:
{{decision: different_page, reason: This is not a forms page}}
"""
    response = review_question_process_llm3.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    print(f"new tokens: {new_tokens}")
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        state["action"] = "exit"
        state["leaving_reason"] = f"The cost extended above $0.10 at the review signup page process with the total being ${total_cost}"
    answers = response["parsed"]
    print(f"Review Answers: {answers}")
    decision = answers["decision"]
    return state, decision

def action_process(ai_answers: list[dict], boxes_details: list[dict], state: ApplicationState, full_page_width: int, full_page_height: int, white_x=None, white_y=None, process=None):
    ai_answers.sort(key=lambda x: {"skip": 0, "fill": 1, "fill_with_time": 2, "delete": 3, "delete_and_fill": 4, "click": 5, "upload_resume": 6, "upload_cover_letter": 7, "markdown": 8, "click_and_view": 9, "submit": 10}.get(x[0].lower(), 999))
    for i in range(len(ai_answers)):
        current_answer = ai_answers[i]
        action = current_answer[0] if len(current_answer ) > 0 else None
        if not action or action == "skip":
            continue
        icon = current_answer[1] if len(current_answer ) > 1 else None
        if not icon:
            continue
        current_box = boxes_details[icon]
        state = execute_action(current_answer=current_answer, current_box=current_box, state=state, full_page_width=full_page_width, full_page_height=full_page_height, white_x=white_x, white_y=white_y, process=process)
    return state

def find_icon(current_answer: dict, state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    new_box = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        box_type = current_box["type"]
        bbox = current_box["content"]
        content = current_box["content"]
        new_box.append([box_type, bbox, content])
    prompt = f"""
You are an AI Applicant helper and will be helping us find the icon from the current_answer.
Look at the boxes_details to determine the icon we will be clicking.


current_answer: {current_answer}

boxes_details: {new_box}

Example output:
{{
icon: 48
}}
"""
    response = find_icon_process_llm3.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    print(f"new tokens: {new_tokens}")
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        state["action"] = "exit"
        state["leaving_reason"] = f"The cost extended above $0.10 at the find icon page process with the total being ${total_cost}"
    decision = response["parsed"]
    icon = decision.get("icon")
    print(f"find icon: {icon}")
    if not icon:
        return None, None, None, state
    current_box = boxes_details[icon]
    coordinates = current_box["bbox"]
    page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    return encoded_bytes, page_x, page_y, state

def execute_action(current_answer: list, current_box: dict, full_page_width: int, full_page_height: int, state: ApplicationState, white_x=None, white_y=None, process=None):
    page = state["current_page"]["page"]
    action = current_answer[0] if len(current_answer ) > 0 else None
    if not action or action == "skip":
        return state
    icon = current_answer[1] if len(current_answer ) > 1 else None
    if not icon or not isinstance(icon, int):
        return state
    coordinates = current_box.get("bbox")
    if not coordinates:
        return state
    page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    if action == "fill":
        action_text = current_answer[2] if len(current_answer ) > 2 else None
        if not action_text:
            return state
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        page.keyboard.type(action_text)
        time.sleep(0.1)
        page.keyboard.press("Enter")
        time.sleep(0.1)
        if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
            page.mouse.click(white_x, white_y)
            time.sleep(1)
        return state
    if action == "delete":
        page.mouse.click(page_x, page_y)
        time.sleep(1)
        for i in range(500):
            page.keyboard.press("ArrowRight")
        for i in range(500):
            page.keyboard.press("Backspace")
    if action == "delete_and_fill":
        action_text = current_answer[2] if len(current_answer ) > 2 else None
        if not action_text:
            return state
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        for i in range(500):
            page.keyboard.press("ArrowRight")
        for i in range(500):
            page.keyboard.press("Backspace")
        page.keyboard.type(action_text)
        time.sleep(0.1)
        page.keyboard.press("Enter")
        time.sleep(0.1)
        if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
            page.mouse.click(white_x, white_y)
    if action == "fill_with_time":
        action_text = current_answer[2] if len(current_answer ) > 2 else None
        if not action_text:
            return state
        page.mouse.click(page_x, page_y)
        page.keyboard.press("ArrowLeft")
        time.sleep(0.2)
        page.keyboard.type(action_text)
        time.sleep(0.2)
        page.keyboard.press("Enter")
        time.sleep(0.2)
        if white_x and white_y:
            page.mouse.click(white_x, white_y)
            time.sleep(1)
        return state
    if action == "click":
        context = page.context
        page_count = len(context.pages)
        page.mouse.click(page_x, page_y)
        time.sleep(1)
        if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
            page.mouse.click(white_x, white_y)
            time.sleep(1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        return state
    if action == "upload_resume":
        user_id = state.get("user_id")
        print(f"user_id: {user_id}")
        application_path = "/Users/peytonrivers/application"
        file_path = f"{user_id}/resume/Resume.pdf"
        file_name = os.path.basename(file_path)
        full_path = os.path.join(application_path, file_name)
        try:
            resume_bytes = supabase.storage.from_("user-files").download(file_path)
        except Exception:
            print("resume bytes did not work")
            return state
        encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        if (page_x is not None and page_y is not None and math.isfinite(page_x) and math.isfinite(page_y)):
            with open(full_path, 'wb') as f:
                f.write(resume_bytes)
            time.sleep(1)
            page.mouse.click(page_x, page_y)
            upload_prompt = 'tell application "Finder" to set target to front window of folder "application" of home'
            run = subprocess.run(["osascript", "-e", ])
            run = subprocess.run(["osascript", "-e", upload_prompt])
            """pyautogui.moveTo(x=350, y=400)
            time.sleep(1)
            pyautogui.click()"""
            time.sleep(1)
            pyautogui.press("right")
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)
            run = subprocess.run(["rm", full_path], capture_output=True)

        return state
    if action == "upload_cover_letter":
        user_id = state.get("user_id")
        file_path = f"{user_id}/resume/Resume.pdf"
        application_path = "/Users/peytonrivers/application"
        file_name = os.path.basename(file_path)
        full_path = os.path.join(application_path, file_name)
        try:
            resume_bytes = supabase.storage.from_("user-files").download(file_path)
        except Exception:
            print("cover letter bytes did not work")
            return state
        encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        if (page_x is not None and page_y is not None and math.isfinite(page_x) and math.isfinite(page_y)):
            with open(full_path, 'wb') as f:
                f.write(resume_bytes)
            time.sleep(1)
            page.mouse.click(page_x, page_y)
            pyautogui.moveTo(x=350, y=400)
            time.sleep(1)
            pyautogui.click()
            pyautogui.press("right")
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)
            run = subprocess.run(["rm", full_path])
        return state
    if action == "markdown":
        pyautogui_image1 = pyautogui.screenshot(region=(100, 40, 1200, 780))
        pyautogui_buffer1 = io.BytesIO()
        pyautogui_image1.save(pyautogui_buffer1, format="PNG")
        old_pyautogui_bytes1 = pyautogui_buffer1.getvalue()
        encoded_pyautogui_bytes1 = base64.b64encode(old_pyautogui_bytes1).decode("utf-8")

        screenshot1 = page.screenshot()
        old_bytes = base64.b64encode(screenshot1).decode("utf-8")
        time.sleep(1)
        pyautogui.moveTo(0, 0)

        time.sleep(1)
        page.mouse.click(page_x, page_y)
        time.sleep(1)
        pyautogui.press("down")
        time.sleep(3)
        body_text = page.locator("body").inner_text()
        state = markdown_process(current_answer=current_answer, encoded_pyautogui_bytes1=encoded_pyautogui_bytes1, old_bytes=old_bytes, body_text=body_text, page_x=page_x, page_y=page_y, state=state, white_x=white_x, white_y=white_y)
        time.sleep(5)
        return state
    if action == "click_and_view":
        screenshot = page.screenshot()
        old_bytes = base64.b64encode(screenshot).decode("utf-8")
        """if not process:
            click_and_view_elements = state.get("click_and_view_elements") 
            click_and_view_index = state.get("click_and_view_index")
        if process:
            print(f"temporary click and view elements: {state.get("temporary_click_and_view_elements")}")
            click_and_view_elements = state.get("temporary_click_and_view_elements")
            click_and_view_index = state.get("temporary_click_and_view_index")
        print(f"click and view elements in execute action: {click_and_view_elements}")
        print(f"click and vivew index: {click_and_view_index}")
        if len(click_and_view_elements) > 0:
            current_element = click_and_view_elements[click_and_view_index]
            click_and_view_index += 1
            if not process:
                state["click_and_view_index"] = click_and_view_index
            if process:
                state["temporary_click_and_view_index"] = click_and_view_index
            current_question = current_element[0]
            click_details = current_element[1]
            icon_status = click_details["icon_status"]
            if icon_status:
                attributes = click_details["attributes"]
                tag = click_details["tag"]
                locator = f"{tag}"
                for key, value in attributes.items():
                    locator += f'[{key}="{value}"]'
                click_element = page.locator(locator).first
                if click_element.count() > 0:
                    box = click_element.evaluate((el) => { return el.getBoundingClientRect(); })
                    middle_x = (box["left"] + box["right"]) / 2
                    middle_y = (box["top"] + box["bottom"]) / 2
                    if (middle_x is not None and middle_y is not None and math.isfinite(middle_x) and math.isfinite(middle_y)):
                        page.mouse.click(middle_x, middle_y)
                        print("Used locator process for click and view")
                        state = click_and_view_process(current_answer=current_answer, old_bytes=old_bytes, state=state, white_x=white_x, white_y=white_y)
                    return state"""
        encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        print("used find icon process for click and view")
        if (page_x is not None and page_y is not None and math.isfinite(page_x) and math.isfinite(page_y)):
            page.mouse.click(page_x, page_y)
        else:
            return state
        state = click_and_view_process(current_answer=current_answer, old_bytes=old_bytes, state=state, white_x=white_x, white_y=white_y)
        time.sleep(1)
        return state
    if action == "submit":
        """if not process:
            submit_element = state.get("submit_element")
        if process:
            submit_element = state.get("temporary_submit_element")
        if submit_element:
            submit_tag = submit_element["tag"]
            attributes = submit_element["attributes"]
            locator = f"{submit_tag}"
            for key, value in attributes.items():
                locator += f'[{key}="{value}"]'
            submit_button = page.locator(locator).first
            if submit_button.count() > 0:
                box = submit_button.evaluate((el) => { return el.getBoundingClientRect(); })
                middle_x = (box["left"] + box["right"]) / 2
                middle_y = (box["top"] + box["bottom"]) / 2
                if (middle_x is not None and middle_y is not None and math.isfinite(middle_x) and math.isfinite(middle_y)):
                    try:
                        with page.expect_popup() as new_page:
                            page.mouse.click(middle_x, middle_y)
                        new_page = new_page.value
                        new_page.wait_for_load_state("load")
                        time.sleep(5)
                        url = new_page.url
                        state["current_page"] = {
                            "page": new_page,
                            "url": url
                        }
                        time.sleep(5)
                        return state
                    except Exception:
                        page.wait_for_load_state("load")
                        time.sleep(5)
                        return state"""
        try:
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
            with page.expect_popup() as new_page:
                page.mouse.click(page_x, page_y)
            new_page = new_page.value
            new_page.wait_for_load_state("domcontentloaded")
            url = new_page.url
            state["current_page"] = {
                "page": new_page,
                "url": url
            }
            time.sleep(5)
            return state
        except Exception:
            page.wait_for_load_state("domcontentloaded")
            time.sleep(5)
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

def cropped_image_process(encoded_image1: str, encoded_image2: str, process=None, submit=None):
    decoded_image1 = base64.b64decode(encoded_image1.encode("utf-8"))
    decoded_image2 = base64.b64decode(encoded_image2.encode("utf-8"))
    buffer1 = io.BytesIO(decoded_image1)
    buffer2 = io.BytesIO(decoded_image2)
    image1 = Image.open(buffer1)
    image2 = Image.open(buffer2)
    matrix_image1 = np.array(image1)
    matrix_image2 = np.array(image2)
    first_cropped_row = row_change(matrix_image1=matrix_image1, matrix_image2=matrix_image2)
    print(f"First cropped row: {first_cropped_row}")
    if not first_cropped_row and process:
        return None, None, None
    if not first_cropped_row:
        data = {"image_input": encoded_image2, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
        response = requests.post("http://127.0.0.1:8000/image_process", json=data)
        response_data = response.json()
        encoded_bytes = response_data["encoded_bytes"]
        boxes_details = response_data["boxes_details"]
        return encoded_bytes, boxes_details, encoded_image2
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
    decoded_bytes = base64.b64decode(encoded_cropped_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    data = {"image_input": encoded_cropped_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    response_data = response.json()
    encoded_bytes = response_data["encoded_bytes"]
    boxes_details = response_data["boxes_details"]
    encoded_cropped_bytes = boxes_only_process(encoded_bytes=encoded_cropped_bytes, boxes_details=boxes_details)
    deco_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    deco_buffer = io.BytesIO(deco_bytes)
    deco_image = Image.open(deco_buffer)
    cropped_width, cropped_height = deco_image.size
    cropped_height_diff = first_cropped_row - 1
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        box = current_box["bbox"]
        y1 = box[1]
        updated_y1 = (y1 * cropped_height) + cropped_height_diff
        updated_ratio_y1 = updated_y1 / height_image2
        boxes_details[i]["bbox"][1] = updated_ratio_y1
        y2 = box[3]
        updated_y2 = (y2 * cropped_height) + cropped_height_diff
        updated_ratio_y2 = updated_y2 / height_image2
        boxes_details[i]["bbox"][3] = updated_ratio_y2
    print("Normal cropped image process")
    return encoded_bytes, boxes_details, encoded_cropped_bytes

def markdown_process(current_answer: dict, encoded_pyautogui_bytes1: str, old_bytes: str, body_text: str, page_x: float, page_y: float, state: ApplicationState, white_x=None, white_y=None):
    page = state["current_page"]["page"]

    for attempt in range(5):
        pyautogui_image2 = pyautogui.screenshot(region=(100, 40, 1200, 780))
        pyautogui_buffer2 = io.BytesIO()
        pyautogui_image2.save(pyautogui_buffer2, format="PNG")
        pyautogui_bytes2 = pyautogui_buffer2.getvalue()
        encoded_pyautogui_bytes2 = base64.b64encode(pyautogui_bytes2).decode("utf-8")

        screenshot = page.screenshot()
        new_bytes = base64.b64encode(screenshot).decode("utf-8")

        encoded_bytes, boxes_details, encoded_cropped_bytes = cropped_image_process(encoded_image1=encoded_pyautogui_bytes1, encoded_image2=encoded_pyautogui_bytes2, process="markdown")
        if not encoded_bytes or not boxes_details or not encoded_cropped_bytes:
            print(f"pyautogui process did not have any difference")
            encoded_bytes, boxes_details, encoded_cropped_bytes = cropped_image_process(encoded_image1=old_bytes, encoded_image2=new_bytes)

        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
        new_box = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            content = current_box["content"]
            new_box.append([icon, box_type, content])
        decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
        buffer = io.BytesIO(decoded_bytes)
        image = Image.open(buffer)
        prompt = f"""
You're an AI Applicant Helper that is in the markup process.

Markdown definition: markdown - Used when clicking an element opens a list of selectable options, such as a dropdown, combobox, menu, or similar selection component. The markdown process is responsible for opening the element, discovering the available options, and selecting the correct option.

You're goal is to look at the the body text + the image to find all the options for the question we are in.

current_question: {current_answer}
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
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_cropped_bytes}"}}
                ]
            }
        ])

        details = response["raw"]
        print(f"AI Details: {details}")
        new_tokens, model_name = details_process(details=details)

        state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
        total_cost = state["token_usage"]["total_cost"]
        if total_cost > 0.10:
            state["action"] = "exit"
            state["leaving_reason"] = f"The cost extended above $0.10 at the markdown page process with the total being ${total_cost}"

        decision = response["parsed"]

        print(f"Markdown decision: {decision}")

        options = decision["options"]
        option_choice = decision["option_choice"]
        current_option = decision["current_option"]

        arrow_count = option_choice - current_option

        print(f"How many times we need to move the arrow: {arrow_count}")

        if arrow_count == 0:
            pyautogui.press("down")
            pyautogui.press("up")
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
            break

        elif markdown_status == "more_questions":
            return state

        elif markdown_status == "incorrect_and_box_closed":
            page.mouse.click(page_x, page_y)
            time.sleep(1)
            body_text = page.locator("body").inner_text()
            continue

        elif markdown_status == "incorrect_and_box_open":
            body_text = page.locator("body").inner_text()
            continue

        elif markdown_status == "more_markdown":
            body_text = page.locator("body").inner_text()
            continue

        else:
            continue
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    coordinates = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        coordinate = current_box["bbox"]
        coordinates.append(coordinate)
    white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    if white_x and white_y:
        page.mouse.click(white_x, white_y)
        time.sleep(2)
    return state

def review_markdown_process(current_answer: list, body_text: str, page_x: float, page_y: float, state: ApplicationState):
    time.sleep(2)
    page = state["current_page"]["page"]
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
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
}}

Ex 2:
{{
markdown_status: incorrect_and_box_open
}}

Ex 3:
{{
markdown_status: incorrect_and_box_closed
}}

Ex 4:
{{
markdown_status: more_markdown
}}

Ex 5:
{{
markdown_status: more_questions
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
    response = review_markdown_process_llm3.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    print(f"new tokens: {new_tokens}")
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        state["action"] = "exit"
        state["leaving_reason"] = f"The cost extended above $0.10 at the review markdown page process with the total being ${total_cost}"
    decision = response["parsed"]
    print(f"Markdown decision: {decision}")
    markdown_status = decision["markdown_status"]
    return markdown_status, state

def click_and_view_process(current_answer: list, old_bytes: str, state: ApplicationState, white_x=None, white_y=None):
    page = state["current_page"]["page"]
    all_boxes = []
    for attempt in range(5):
        print(f"Click and view attempt: {attempt + 1}")
        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
        encoded_bytes, boxes_details, ecoded_cropped_bytes = cropped_image_process(encoded_image1=old_bytes, encoded_image2=encoded_bytes)
        current_question = current_answer[2] if len(current_answer) > 2 else None
        new_box = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            content = current_box["content"]
            new_box.append([icon, box_type, content])
        all_boxes.append(new_box)

        prompt = f"""
You are completing only the section revealed by a click_and_view action in a job application.

CURRENT SECTION
{current_question}

GOAL
- Correctly answer every required question.
- Fix visible validation errors.
- Leave already-correct answers unchanged.
- Use the user's profile first and reasonable inference when necessary.
- Return an action for every relevant visible question.
- Use the input/option icon, not the question-label icon, when possible.

ACTIONS
skip: No change needed or question should be skipped.
fill: Fill an empty input. Requires action_text + icon.
fill_with_time: Fill a date/time input. Requires action_text + icon.
delete: Clear incorrect/unwanted text. Requires icon.
delete_and_fill: Replace existing text. Requires action_text + icon.
click: Select/unselect an immediately answerable option. Requires icon.
upload_resume: Resume upload field. Requires icon.
upload_cover_letter: Cover-letter upload field. Requires icon.
click_and_view: Click only when it reveals additional fields/questions that must be completed. Requires icon + question.
markdown: Dropdown/combobox/menu requiring option discovery and selection. Requires icon + current_question.

IMPORTANT
- Handle only questions/fields revealed by this section.
- add_option should be true when we need to add more information in this section and add_option should be false when we don't need to add more information in this section
- Use submit action for when we are adding more information in this section.
- Ignore unrelated fields that existed before it opened.
- Fix visible errors inside this section.
- Leave correct existing answers unchanged.
- Use the user's profile first and reasonable inference when necessary.
- Use the input/option icon, not the question-label icon, when possible.
- Use submit only for a Save/Add/Done/Confirm/Continue control belonging to this section.
- Use delete or delete and fill if one of the inputted answers is incorrect.

ITEMS ELEMENTS

skip: [action]

fill: [action, icon, action_text]

fill_with_time: [action, icon, action_text]

delete: [action, icon]

delete_and_fill: [action, icon, action_text]

click: [action, icon]

upload_resume: [action, icon]

upload_cover_letter: [action, icon]

click_and_view: [action, icon, current_question]

markdown: [action, icon, current_question]

submit: [action, icon]

ACTIONS

Example:

items: [["skip"], ["fill", 28, {state["email"]}], ["fill_with_time", 35, "08/01/2020"], ["delete", 38], ["delete_and_fill", 42, {state["first_name"]}], ["click", 32], ["upload_resume", 50], ["upload_cover_letter", 52], ["click_and_view", 22, "Add More Work Experience"], ["markdown", 60, "What U.S. State are you in?"], ["submit", 30]]

add_option: True

Page Elements format:
[icon, type, content]

PAGE ELEMENTS
{new_box}

USER PROFILE
email={state["email"]}
password={state["password"]}
name={state["first_name"]} {state["last_name"]}
phone={state["phone_number"]}
address={state["address_line1"]}, {state["address_line2"]}, {state["city"]}, {state["user_state"]} {state["zip_code"]}, {state["country"]}
date={state["date"]}
work_authorized={state["work_authorized"]}
sponsorship={state["requires_sponsorship"]}
veteran={state["veteran"]}
disability={state["disability"]}
linkedin={state["linkedin_url"]}
github={state["github_url"]}
portfolio={state["portfolio_url"]}
work_experience={state["work_experience"]}
education={state["education"]}
resume={state["resume_text"]}
cover_letter={state["cover_letter_text"]}

Set add_option=True only when the section should submit/save this entry and another user entry remains to be added.
Otherwise set add_option=False.

If asked how the job was found, prefer Other/Website/Job Board or the closest equivalent.
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
        new_tokens, model_name = details_process(details=details)
        print(f"new tokens: {new_tokens}")
        state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
        total_cost = state["token_usage"]["total_cost"]
        if total_cost > 0.10:
            state["action"] = "exit"
            state["leaving_reason"] = f"The cost extended above $0.10 at the click and view page process with the total being ${total_cost}"
        answers = response["parsed"]
        ai_answers = answers["items"]
        print(f"AI Answers: {ai_answers}")
        temporary_submit_index = None
        temporary_click_and_view_elements = []
        temporary_click_and_view_index = 0
        state["temporary_click_and_view_index"] = temporary_click_and_view_index
        for i in range(len(ai_answers)):
            current_ans = ai_answers[i]
            action = current_ans[0] if len(current_ans) > 0 else None
            print(f"action: {action}")
            if action == "click_and_view":
                current_click = []
                current_click.append(current_ans)
                current_click_icon = current_ans[1] if len(current_ans) > 1 else None
                if current_click_icon is None:
                    current_click.append({"icon_status": None})
                    temporary_click_and_view_elements.append(current_click)
                    continue
                coordinates = boxes_details[current_click_icon]["bbox"]
                page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
                if (page_x is not None and page_y is not None and math.isfinite(page_x) and math.isfinite(page_y)):
                    page.mouse.click(page_x, page_y, button="right")
                    current_click_element = page.evaluate("""
                                () => {
                                    const el = document.activeElement;
                                    const box = el.getBoundingClientRect();
                    
                                    return {
                                        tag: el.tagName.toLowerCase(),
                    
                                        attributes: Object.fromEntries(
                                            Array.from(el.attributes).map(attr => [
                                                attr.name,
                                                attr.value
                                            ])
                                        ),
                    
                                        text: el.innerText,
                    
                                        bounding_box: {
                                            x: box.x,
                                            y: box.y,
                                            width: box.width,
                                            height: box.height
                                        },
                    
                                        center: {
                                            x: box.x + box.width / 2,
                                            y: box.y + box.height / 2
                                        }
                                    };
                                }
                            """)
                    current_click_element["icon_status"] = True
                    print(f"Current click element: {current_click_element}")
                    current_click.append(current_click_element)
                    temporary_click_and_view_elements.append(current_click)
                    if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
                        page.mouse.click(white_x, white_y)
                else:
                    current_click.append({"icon_status": False})
                    temporary_click_and_view_elements.append(current_click)
            
            if action == "submit":
                print(f"submit answer: {current_ans}")
                submit_icon = current_ans[1] if len(current_ans) > 1 else None
                if submit_icon is None:
                    continue
                coordinates = boxes_details[submit_icon]["bbox"]
                page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
                if (page_x is not None and page_y is not None and math.isfinite(page_x) and math.isfinite(page_y)):
                    page.mouse.click(page_x, page_y, button="right")
                    temporary_submit_element = page.evaluate("""
                                () => {
                                    const el = document.activeElement;
                                    const box = el.getBoundingClientRect();
                    
                                    return {
                                        tag: el.tagName.toLowerCase(),
                    
                                        attributes: Object.fromEntries(
                                            Array.from(el.attributes).map(attr => [
                                                attr.name,
                                                attr.value
                                            ])
                                        ),
                    
                                        text: el.innerText,
                    
                                        bounding_box: {
                                            x: box.x,
                                            y: box.y,
                                            width: box.width,
                                            height: box.height
                                        },
                    
                                        center: {
                                            x: box.x + box.width / 2,
                                            y: box.y + box.height / 2
                                        }
                                    };
                                }
                            """)
                    print(f"Submit Element: {temporary_submit_element}")
                    temporary_submit_index = i
                    state["temporary_submit_element"] = temporary_submit_element
                    if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
                        page.mouse.click(white_x, white_y)
        if temporary_submit_index == None:
            state["temporary_submit_element"] = None
        if len(temporary_click_and_view_elements) == 0:
            state["temporary_click_and_view_elements"] = []
        else:
            state["temporary_click_and_view_elements"] = temporary_click_and_view_elements

        answers = response["parsed"]
        ai_answers = answers["items"]
        add_option = answers["add_option"]
        state = action_process(ai_answers=ai_answers, boxes_details=boxes_details, state=state, white_x=white_x, white_y=white_y, process="temporary")
        if add_option == True:
            continue
        click_and_view_status, state = review_click_and_view_process(current_answer=current_answer, old_bytes=old_bytes, state=state)
        if click_and_view_status == "complete":
            break
    return state

def review_click_and_view_process(
    current_answer: list,
    old_bytes: str,
    state: ApplicationState
):
    time.sleep(2)

    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    encoded_bytes, boxes_details, encoded_cropped_bytes = cropped_image_process(encoded_image1=old_bytes, encoded_image2=encoded_bytes)


    prompt = f"""
You're an AI Applicant Helper.

Your specific task is Click and View Reviewer.

CLICK AND VIEW DEFINITION:

click_and_view is used when clicking an element reveals additional
information, questions, fields, or a new section that needs to be
completed.

The original click_and_view question was:

{current_answer}

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

{current_answer}

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
}}


EXAMPLE 2:

{{
    click_and_view_status: more_questions,
}}


EXAMPLE 3:

{{
    click_and_view_status: incorrect,
}}
"""

    response = review_click_and_view_process_llm3.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])

    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    print(f"new tokens: {new_tokens}")
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    total_cost = state["token_usage"]["total_cost"]
    if total_cost > 0.10:
        state["action"] = "exit"
        state["leaving_reason"] = f"The cost extended above $0.10 at the review click and view page process with the total being ${total_cost}"

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
GPA: 4.0

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
graph.add_conditional_edges("signup_process", signup_routing, {"max_tries": END, "total_cost": END, "new_form": "signup_process", "different_page": "decide_page", "decide_page": "decide_page"})
graph.add_edge("wait_process", "decide_page")
graph.add_conditional_edges("wait_process", wait_routing, {"continue": "decide_page", "exit": END})

mapping = graph.compile()

def complete_application(url2: str):
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        context.add_init_script("""
            document.addEventListener(
                "contextmenu",
                event => {
                    event.preventDefault();
                    event.stopPropagation();
                },
                true
            );
        """)
        page = context.new_page()
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
        user_id = "76f6e1cd-85de-46f7-b4c7-074284b3a1cc"
        time.sleep(5)
        final_state = mapping.invoke({"url": url2, "current_page": current_page, "token_usage": token_usage, "browser": browser, "context": context, "user_id": user_id})
        print(f"final_state: {final_state}")
        leaving_reason = final_state.get("leaving_reason")
        print(f"Browser closing due to : {leaving_reason}")
        browser.close()
try:
    complete_application(url)
except Exception as e:
    print(f"error: {e}")

print("hello world")