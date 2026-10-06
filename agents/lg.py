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
from agents.state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess, AITokens, QuestionProcess, AnswerItem, MarkdownProcess, ReviewMarkdownProcess, CompleteMarkdownProcess, ReviewClickAndViewProcess, FindIcon, ReviewQuestionProcess, SearchProcess, ReviewSearchProcess, CompleteSearchProcess, TextTimeProcess, ReviewTimeProcess, CalendarTimeProcess
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests
import cv2
import math
import subprocess
from database.storage import supabase
from datetime import date

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
MODEL_NAME2 = "gpt-6-luna"

llm = ChatOpenAI(model=MODEL_NAME, temperature=0.3, api_key=openai_key)
llm2 = ChatOpenAI(model=MODEL_NAME2, reasoning_effort="high", api_key=openai_key)
llm3 = ChatOpenAI(model=MODEL_NAME2, api_key=openai_key)

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
review_markdown_process_llm2 = llm2.with_structured_output(ReviewMarkdownProcess, include_raw=True)
complete_markdown_process_llm2 = llm2.with_structured_output(CompleteMarkdownProcess, include_raw=True)
review_click_and_view_process_llm3 = llm3.with_structured_output(ReviewClickAndViewProcess, include_raw=True)
find_icon_process_llm3 = llm3.with_structured_output(FindIcon, include_raw=True)
search_process_llm2 = llm2.with_structured_output(SearchProcess, include_raw=True)
review_search_process_llm2 = llm2.with_structured_output(ReviewSearchProcess, include_raw=True)
complete_search_process_llm2 = llm2.with_structured_output(CompleteSearchProcess, include_raw=True)
text_time_process_llm2 = llm2.with_structured_output(TextTimeProcess, include_raw=True)
review_time_process_llm2 = llm2.with_structured_output(ReviewTimeProcess, include_raw=True)
calendar_time_process_llm2 = llm2.with_structured_output(CalendarTimeProcess, include_raw=True)

url = "https://www.allstate.jobs/job/23890328/software-engineering-manager-java-/"
url = "https://testing-kohl-psi.vercel.app/"
print(url.title)
model_ratios = [["gpt-5.4-nano", 0.20 / 1000000, 1.25 / 1000000, 0.02 / 1000000], ["gpt-5.6-luna", 0.20 / 1000000, 1.20 / 1000000, 0.02 / 1000000], ["gpt-6-luna", 0.10 / 1000000, 0.50 / 1000000, 0.01 / 1000000]]


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
    new_cached_tokens_cost = new_cached_tokens * cached_cost
    print(f"new input token details: {new_tokens["input_token_details"]}")
    print(f"new cached tokens: {new_cached_tokens}")
    after_new_input_tokens = new_input_tokens - new_cached_tokens
    new_input_token_cost = after_new_input_tokens * input_cost
    print(new_input_tokens)
    new_output_tokens = new_tokens["output_tokens"]
    print(f"new output tokens: {new_output_tokens}")
    new_output_tokens_cost = new_output_tokens * output_cost
    new_total_cost = new_cached_tokens_cost + new_input_token_cost + new_output_tokens_cost
    print(f"Current iteration cost: ${new_total_cost}")
    input_tokens += after_new_input_tokens
    print(f"Total input tokens: {input_tokens}")
    cached_tokens += new_cached_tokens
    print(f"Total cached tokens: {cached_tokens}")
    output_tokens += new_output_tokens
    print(f"Total output tokens: {output_tokens}")
    total = total_cost + new_total_cost
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
    print(f"details: {details}")
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
    page.set_viewport_size({"width": 1300, "height": real_height})
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
    context = state["context"]
    print(f"context: {context}")
    print(f"context pages: {context.pages}")
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

    previous_answers = []

    for attempt in range(5):
        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
        encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
        encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)
        decoded_bytes2 = base64.b64decode(encoded_bytes2.encode("utf-8"))
        buffer = io.BytesIO(decoded_bytes2)
        image = Image.open(buffer)
        page_elements = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            bbox = current_box["bbox"]
            coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
            box_type = current_box["type"]
            content = current_box["content"]
            page_elements.append([icon, box_type, coordinates, content])
    
        coordinates = []
        for coord in range(len(boxes_details)):
            current_box = boxes_details[coord]
            coordinate = current_box["bbox"]
            coordinates.append(coordinate)
        white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
        
        prompt = f"""
You are completing a job application form using the user's profile and the visible page.
You need to look at the images to think logically on how to answer the questions and deal with errors.


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
time: Any question that has anything to due with time. Requires icon + current_question. Never click the calendar icon but always choose the text icon instead.
delete: Clear incorrect/unwanted text. Requires icon.
click: Select/unselect an immediately answerable option. Requires icon.
search: When you need to search something or enter skills that could possibly add suggested drop downs, search texts must always be one word.
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
- You need to look at the images to think logically on how to answer the questions and deal with errors.

Page Elements format
[icon, type, coordinates, content text]

PAGE ELEMENTS
{page_elements}

ITEMS ELEMENTS

skip: [action]

fill: [action, icon, action_text]

delete: [action, icon]

click: [action, icon]

time: [action, icon, current_question]

search: [action, icon, current_question, list of text]

upload_resume: [action, icon]

upload_cover_letter: [action, icon]

click_and_view: [action, icon, current_question]

markdown: [action, icon, current_question]

submit: [action, icon, submit_text]

ACTIONS

Example:

items: [["skip"], ["fill", 28, {state["email"]}], ["fill_with_time", 35, "08/01/2020"], ["delete", 38], ["delete_and_fill", 42, {state["first_name"]}], ["click", 32], ["search", ["python", "playwright", "java"]], ["search", 8, "What skills do you have", ["skill 1", "skill 2", "skill 3"]], ["upload_resume", 50], ["upload_cover_letter", 52], ["click_and_view", 22, "Add More Work Experience"], ["markdown", 60, "What U.S. State are you in?"], ["submit", 30]]
error: yes there was an error on checking a box and I handled it by clicking a box to fix it.


PREVIOUS ANSWERS TO HELP WITH ERROR HANDLING
[{previous_answers}]

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
        previous_answers.append(ai_answers)
        print(f"AI Answers: {ai_answers}")
        context = state.get("context")
        page_count = len(context.pages)
        state = action_process(ai_answers=ai_answers, boxes_details=boxes_details, state=state, full_page_width=full_page_width, full_page_height=full_page_height, white_x=white_x, white_y=white_y, page_count=page_count)
        state, decision = review_answer_question_process(state=state, all_text=all_text)
        del all_text[-1]
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
    print(f"all text: {all_text}")
    print(f"all text count: {len(all_text)}")
    prompt = f"""
Your an AI Applicant helper and your job is to look at the two different lists of body text and determine.
1. same_form - all the body text look similar.
2. new_form - The old forms page is complete and we are on a new forms page with the body text looking different.
3. different_page - this is niether the old forms page and not a new forms page as well and is instead something different

All text:
{all_text}

Ex 1:
{{decision: same_form}}

Ex 2:
{{decision: new_form}}

Ex 3:
{{decision: different_page}}
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

def action_process(ai_answers: list[list], boxes_details: list[dict], state: ApplicationState, full_page_width: int, full_page_height: int, white_x=None, white_y=None, process=None, page_count=None):
    ai_answers.sort(key=lambda x: {"skip": 0, "fill": 1, "delete": 2, "click": 3, "time": 4, "search": 5, "upload_resume": 6, "upload_cover_letter": 7, "markdown": 8, "click_and_view": 9, "add_more": 10, "submit": 11}.get(x[0].lower(), 999))
    click_and_view_count = 0
    print(f"ai answers: {ai_answers}")
    for l in range(len(ai_answers)):
        current_answer = ai_answers[l]
        print(f"current answer: {current_answer}")
        action = current_answer[0] if len(current_answer) > 0 else None
        if action == "click_and_view":
            click_and_view_count += 1
    state["click_and_view_count"] = click_and_view_count
    state["current_click_and_view_count"] = 0
    for i in range(len(ai_answers)):
        current_answer = ai_answers[i]
        action = current_answer[0] if len(current_answer ) > 0 else None
        if not action or action == "skip":
            continue
        icon = current_answer[1] if len(current_answer ) > 1 else None
        if not icon:
            continue
        if type(icon) == int and icon >= 0:
            current_box = boxes_details[icon]
        else:
            current_box = -1
        state = execute_action(current_answer=current_answer, current_box=current_box, state=state, full_page_width=full_page_width, full_page_height=full_page_height, white_x=white_x, white_y=white_y, process=process, click_and_view_count=click_and_view_count, page_count=page_count)
    return state

def find_icon(current_answer: dict, state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4),]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])
    prompt = f"""
You are an AI Applicant helper and will be helping us find the icon from the current_answer.
Look at the boxes_details to determine the icon we will be clicking.

Often times you will be in the forms process so looking at the the action type will help you determine what element we are looking for, think logically to find the icon we are looking for.

current_answer: {current_answer}

PAGE ELEMENTS FORMAT
[icon, type, coordinates, content]

Page elements: {page_elements}

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

def execute_action(current_answer: list, current_box: dict, full_page_width: int, full_page_height: int, page_count: int, state: ApplicationState, white_x=None, white_y=None, process=None, click_and_view_count=None, ai_answers=None):
    page = state["current_page"]["page"]
    context = state.get("context")
    action = current_answer[0] if len(current_answer ) > 0 else None
    if not action or action == "skip":
        return state
    if action != "arrow":
        icon = current_answer[1] if len(current_answer ) > 1 else None
        if not icon or not isinstance(icon, int):
            return state
        if icon >= 0:
            coordinates = current_box.get("bbox")
            page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    context = state.get("context")

    if action == "fill":
        action_text = current_answer[2] if len(current_answer ) > 2 else None
        if not action_text:
            action_text = ""
        for i in range(1000):
            page.keyboard.press("Backspace")
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        time.sleep(0.1)
        page.keyboard.type(action_text)
        time.sleep(0.1)
        page.keyboard.press("Enter")
        time.sleep(0.1)
        if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
            page.mouse.click(white_x, white_y)
            time.sleep(1)
    elif action == "delete":
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        time.sleep(1)
        for i in range(500):
            page.keyboard.press("ArrowRight")
        for i in range(500):
            page.keyboard.press("Backspace")
    elif action == "delete_and_fill":
        action_text = current_answer[2] if len(current_answer ) > 2 else None
        if not action_text:
            action_text = ""
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
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
            time.sleep(0.1)
            new_page_count = len(context.pages)
            if new_page_count > page_count:
                all_pages = context.pages
                all_pages[-1].close()
    elif action == "white_pixel":
        pyautogui_image = pyautogui.screenshot(region=(25, 120, full_page_width, 700))
        buffer = io.BytesIO()
        pyautogui_image.save(buffer, format="PNG")
        pyautogui_bytes = buffer.getvalue()
        encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
        data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
        response = requests.post("http://127.0.0.1:8000/image_process", json=data)
        data = response.json()
        boxes_details = data["boxes_details"]
        coordinates = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            coordinate = current_box["bbox"]
            coordinates.append(coordinate)
        white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, coordinates=coordinates, full_page_width=full_page_width, full_page_height=580)
        white_x += 25
        white_y += 120
        print(f"white x: {white_x}, white y: {white_y}")
        pyautogui.click(x=white_x, y=white_y)
        time.sleep(0.1)
        pyautogui.moveTo(0, 0)
    elif action == "time":
        current_question = current_answer[2] if len(current_answer ) > 2 else None
        current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if current_height != full_page_height:
            print("used find icon for time")
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        page.mouse.click(page_x, page_y)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        state = time_process(current_question=current_question, full_page_width=current_height, page_x=page_x, page_y=page_y, state=state)
    elif action == "click":
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
            page.mouse.click(white_x, white_y)
            time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
    elif action == "arrow":
        current_option = current_answer[1]
        option_choice = current_answer[2]
        option_difference = option_choice - current_option
        if option_difference == 0:
            pyautogui.hotkey("down")
            pyautogui.hotkey("up")
            pyautogui.hotkey("enter")

        elif option_difference > 0:
            for i in range(option_difference):
                pyautogui.hotkey("down")
            time.sleep(0.1)
            pyautogui.hotkey("enter")
        else:
            for i in range(abs(option_difference)):
                pyautogui.hotkey("up")
            time.sleep(0.1)
            pyautogui.hotkey("enter")
    elif action == "exit":
        page.mouse.click(page_x, page_y)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            page_difference = new_page_count - page_count
            for i in range(page_difference):
                all_pages = context.pages
                all_pages[-1].close()

    elif action == "upload_resume":
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
        current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if current_height != full_page_height:
            print("used find icon for upload resume")
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        if (page_x is not None and page_y is not None and math.isfinite(page_x) and math.isfinite(page_y)):
            with open(full_path, 'wb') as f:
                f.write(resume_bytes)
            time.sleep(0.1)
            page.mouse.click(page_x, page_y)
            new_page_count = len(context.pages)
            if new_page_count > page_count:
                all_pages = context.pages
                all_pages[-1].close()
            upload_prompt = 'tell application "Finder" to set target to front window of folder "application" of home'
            run = subprocess.run(["osascript", "-e", ])
            run = subprocess.run(["osascript", "-e", upload_prompt])
            """pyautogui.moveTo(x=350, y=400)
            time.sleep(1)
            pyautogui.click()"""
            time.sleep(1)
            pyautogui.press("right")
            time.sleep(0.5)
            pyautogui.press("right")
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(3)
            run = subprocess.run(["rm", full_path], capture_output=True)

    elif action == "upload_cover_letter":
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
        current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if current_height != full_page_height:
            print("used find icon for upload cover letter")
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        if (page_x is not None and page_y is not None and math.isfinite(page_x) and math.isfinite(page_y)):
            with open(full_path, 'wb') as f:
                f.write(resume_bytes)
            time.sleep(0.1)
            page.mouse.click(page_x, page_y)
            new_page_count = len(context.pages)
            if new_page_count > page_count:
                all_pages = context.pages
                all_pages[-1].close()
            pyautogui.moveTo(x=350, y=400)
            time.sleep(1)
            pyautogui.click()
            pyautogui.press("right")
            time.sleep(0.5)
            pyautogui.press("right")
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)
            run = subprocess.run(["rm", full_path])
    elif action == "markdown":
        pyautogui.moveTo(0, 0)
        time.sleep(1)
        current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if current_height != full_page_height:
            print("used find icon for markdown")
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        time.sleep(1)
        pyautogui.press("down")
        time.sleep(3)
        state = markdown_process(current_answer=current_answer, ai_answers=ai_answers, state=state)
        time.sleep(5)
    elif action == "click_and_view":
        current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if current_height == full_page_height:
            print("height is equal in click and view")
        if current_height != full_page_height:
            print("used find icon for click and view")
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        current_click_and_view_count = state.get("current_click_and_view_count")
        print(f"current click and view count: {current_click_and_view_count}")
        if current_click_and_view_count:
            current_click_and_view_count += 1
        else:
            current_click_and_view_count = 1
        state["current_click_and_view_count"] = current_click_and_view_count
        print(f"new click and view count: {current_click_and_view_count}")
        if click_and_view_count and click_and_view_count == current_click_and_view_count:
            print("sending to click and view process")
            state = click_and_view_process(state=state)
    elif action == "search":
        pyautogui.moveTo(0, 0)
        page.mouse.click(page_x, page_y)
        current_question = current_answer[2]
        all_text = current_answer[-1]
        current_text = all_text[0]
        for i in range(1000):
            page.keyboard.press("Backspace")
        page.keyboard.type(current_text)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        state = search_process(all_text=all_text, current_question=current_question, ai_answers=ai_answers, state=state)
    elif action == "add_more":
        current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if current_height != full_page_height:
            print("used find icon for add more")
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        page.mouse.click(page_x, page_y)
        time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        if (white_x is not None and white_y is not None and math.isfinite(white_x) and math.isfinite(white_y)):
            page.mouse.click(white_x, white_y)
            time.sleep(0.1)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()     
    elif action == "submit":
        try:
            current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.documentElement.scrollHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
            if current_height == full_page_height:
                print("height is equal in the submit action")
            if current_height != full_page_height:
                print("used find icon for submit")
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
    time.sleep(1)
    print(f"all pages: {context.pages}")
    new_page_count = len(context.pages)
    print(f"page count: {page_count}")
    print(f"new page count: {new_page_count}")
    delete_count = new_page_count - page_count
    print(f"delete count: {delete_count}")
    if delete_count != 0:
        while new_page_count > page_count:
            all_pages = context.pages
            print(f"all pages: {all_pages}")
            all_pages[-1].close()
            time.sleep(0.5)
            print(f"new all pages: {context.pages}")
            new_page_count = len(context.pages)
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

def time_process(current_question: str, full_page_width: int, page_x: int, page_y: int, state: ApplicationState):
    page = state["current_page"]["page"]
    state, desired_date, encoded_pyautogui_bytes = text_time_process(current_question=current_question, full_page_width=full_page_width, state=state)
    state, text_inputted, image1, image2, complete = review_time_process(current_question=current_question, desired_date=desired_date, encoded_pyautogui_bytes=encoded_pyautogui_bytes, state=state)
    if complete:
        return state
    has_type = False
    active_element = page.locator(":focus")
    if active_element.count() == 0:
        active_element = None
    else:
        active_element = active_element.first
    if active_element:
        has_type = active_element.get_attribute("type") in ["date", "month"]
        if has_type:
            desired_date = datetime.strptime(desired_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            active_element.fill(desired_date) 
            state, text_inputted, image1, image2, complete = review_time_process(current_question=current_question, desired_date=desired_date, encoded_pyautogui_bytes=encoded_pyautogui_bytes, state=state)
    if complete:
        return state
    
    if text_inputted:
        if not has_type:
            state, desired_date, do_not_use_bytes = text_time_process(current_question=current_question, full_page_width=full_page_width, state=state)
            state, text_inputted, image1, image2, complete = review_time_process(current_question=current_question, desired_date=desired_date, encoded_pyautogui_bytes=encoded_pyautogui_bytes, state=state)
    
    if image1 and not image2:
        page.mouse.click(page_x, page_y)

    for attempt in range(4):
        state, complete = calendar_time_process(current_question=current_question, desired_date=desired_date, image1=image1, image2=image2, full_page_width=full_page_width, page_x=page_x, page_y=page_y, state=state)
        if complete:
            return state
    
    return state

def text_time_process(current_question: str, full_page_width: int, state: ApplicationState):
    page = state["current_page"]["page"]
    pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 780))
    buffer = io.BytesIO()
    pyautogui_image.save(buffer, format="PNG")
    pyautogui_bytes = buffer.getvalue()
    encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    data = response.json()
    encoded_pyautogui_bytes = data["encoded_bytes"]
    boxes_details = data["boxes_details"]
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    """decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image.show()"""

    prompt = f"""
You're an AI Applicant in the Fill time with text process.

Steps to Fill out the time process

current question: {current_question}

Fill current question: {current_question} Time Process.
1. Find the Current Question we are on and only look at the current question.
2. Find what position we are highlighted in the current question.
3. Look at the highlighted text within the current question and determine how many moves left we need to be to be at the left-most position in the time text.
4. Answer the current question by using the USER PROFILE

Response Template
- action: This tells us what action we are going to use to fill this text
- left_arrow: This tells us how many arrows left we need to move to be at the left most postion
- text: This is the exact text we will enter to answer the current question by looking at the USER PROFILE.

Example output 1

{{
    "action": "fill",
    "left_arrow": 2,
    "text": "08/21/2026"

We need to move two positions left to be at the left most position. I answered the current question with the user profile and entered the text in the format the current question wants us to give us in.
}}

Example output 2

{{
    "action": "fill",
    "left_arrow": 0,
    "text": "09/2026"

We are currently at the left most position so we need to move 0 spots left. I answered the question exactly with the text that needed to be inputted in the format of the response guidance.
}}

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
    response = text_time_process_llm2.invoke([
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
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answers = response["parsed"]
    print(f"time text answers: {answers}")
    action = answers.get("action")
    left_arrow = answers.get("left_arrow")
    text = answers.get("text")
    if action:
        for i in range(left_arrow):
            pyautogui.hotkey("left")
        page.keyboard.type(text)
    desired_date = text
    return state, desired_date, encoded_pyautogui_bytes

def review_time_process(current_question: str, desired_date: str, encoded_pyautogui_bytes: str, state: ApplicationState):
    encoded_bytes, boxes_details, full_page_width, full_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    prompt = f"""
You're an AI Applicant helper in the Review Time Process.

You will only be looking at the current question during this process.

Current Question: {current_question}

We will be trying to get the desired date within the respective question response format.

Desired Date: {desired_date}

You will answer this question by following the Review Time Process.

Review Time Process.
1. Your first step is to find the current question {current_question}, and you will only be looking at the current question.
2. Next Determine if there is text inputted in the current question.
- If no text has been inputted then determine if image 1, image 2, both, or neither have the calendar popup in the image.
- Based on which images have or don't have a calendar popup in them we will return something like this.
- Ex: {{"text_inputted": False, "image1": True, "image2": False, "complete": False}}
3. If there is text inputted and it is correct then you will return this.
- {{"text_inputted": True, "complete": True}}
4. If there is text inputted and it is not correct you will return something like this.
- {{"text_inputted": True, "complete": False}}

Example output 1
{{
"text_inputted": True,
"complete": True

On the current question there is text inputted and the text inputted is correct.
}}

Example 2
{{
"text_inputted": True,
"complete": False

There is text inputted but the text inputted is not correct.
}}

Example 3
{{
"text_inputted": False,
"image1": False,
"image2": False,
"complete": False

There is no text inputted and both images do not show a calendar popup.
}}

Example 4
{{
"text_inputted": False,
"image1": True,
"image2": False,
"complete": False

There is no text inputted and image 1 shows a calendar popup but not image 2.
}}

Example 5
{{
"text_inputted": False,
"image1": False,
"image2": True,
"complete": False

There is no text inputted and image 2 shows a calendar popup but image 1 does not show a calendar popup.
}}

Example 6
{{
"text_inputted": False,
"image1": True,
"image2": True,
"complete": False

There is no text inputted and both images show a calendar popup.
}}
"""
    response = review_time_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_pyautogui_bytes}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    print(f"review time process answer: {answer}")
    text_inputted = answer.get("text_inputted")
    image1 = answer.get("image1")
    image2 = answer.get("image2")
    complete = answer.get("complete")
    return state, text_inputted, image1, image2, complete

def day_calculator(current_day: int, current_month: int, current_year: int, desired_day: int, desired_month: int, desired_year: int):
    current_date = date(current_year, current_month, current_day)
    desired_date = date(desired_year, desired_month, desired_day)

    return (desired_date - current_date).days

def calendar_time_process(current_question: str, desired_date: str, image1: bool, image2: bool, full_page_width: int, page_x: int, page_y: int, state: ApplicationState):
    page = state["current_page"]["page"]
    if image2:
        encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    else:
        pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 780))
        buffer = io.BytesIO()
        pyautogui_image.save(buffer, format="PNG")
        pyautogui_bytes = buffer.getvalue()
        encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
        data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
        response = requests.post("http://127.0.0.1:8000/image_process", json=data)
        data = response.json()
        encoded_bytes = data["encoded_bytes"]
        decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
        buffer = io.BytesIO(decoded_bytes)
        image = Image.open(buffer)
        boxes_details = data["boxes_details"]
        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
        

    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])
    prompt = f"""
You're an AI Applicant helper in the Calendar Time Process.

You will only be looking at the current question: {current_question}

We will try to be getting the desired output in the calendar: {desired_date}

If you do not see a calendar in the image immediately stop and return
{{"action": None, "complete": False}}

You will follow the Calendar Time Process to Answer the Question

Calendar Time Process
1. Find the Calendar in the image
2. Find and mark the current date on the calendar, look at the month, the year, and the highlighted day if present to determine the current day. This is extremely important to know the Current date.
    - Ex: "08/12/2029"
    - Ex: "09/2025"
3. Next look at the desired_date: {desired_date}
4. If the calendar is in month Format, meaning that it shows all the months of the year follow this.
    - Determine if our current year matches the desired year.
    - If our current year does not match the desired year, look at the calendar and find the icon that will move us forward or backward to that desired year
    - Return something like this {{"action": click_month, "icon": 45, "desired_month": 5, "current_month": 4, current_year: 1998, desired_year: 2052}}
    - If our current year matches the desired year, then find the icon that will click the month to get us to that desired month.
    - Return something like this {{"action": click_month, "icon": 45, "desired_month": 10, "current_month": 2, current_year: 2002, desired_year: 2002}}
5. If the calendar is in day Format, meaning it shows the days of the month follow this.
    - Return the current day, month, year we are currently at in the calendar popup. Return our desired day, month, year we want to be at
    - Ex: {{"action": arrow_day, "current_day": 15, desired_day: 30, current_month: 2, desired_month: 11, current_year: 2007, desired_year: 2026}}

Actions Format
None: this is when you don't see any calendar popup which causes us to click the calendar again.
click_month: you use this action when you see all the months of the year.
arrow_day: You use this action when you see the days on the calendar.

PAGE ELEMENTS FORMAT
[icon, type, coordinates, content]

Page Elements: {page_elements}

Example output 1
{{
"action": None,
"complete": False

I saw no calendar pop up in the image so I returned the output no action
}}

Example output 2
{{
"action": "arrow_day",
"current_day": 30,
"desired_day": 12,
"current_month": 8
"desired_month": 12
"current_year": 1997
"desired_year": 2048
"complete": False

The calendar shows days with the current day being August 8th 1997 and we are trying to get to the desired date of December 12th 2048.
}}

Example output 3
{{
"action": "click_month",
icon: 94,
"current_month": 8
"desired_month": 2
"current_year": 2028,
"desired_year": 2025

The calendar shows all the months of the year. We need to click the backward arrow to get to the desired year.
}}

Example output 4
{{
"action": "click_month",
icon: 112,
"current_month": 8
"desired_month": 2
"current_year": 2025
"desired_year": 2025

The current year and the desired year are the same. We need to click february to get to our desired month.
}}

Example output 5
{{
"action": "white_pixel",
"icon": -1,
"complete": True

The desired date matches the current date so we choose the white_pixel action which always uses the -1 icon.
}}
"""
    response = calendar_time_process_llm2.invoke([
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
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    action = answer.get("action")
    icon = answer.get("icon")
    current_day = answer.get("current_day")
    current_month = answer.get("current_month")
    current_year = answer.get("current_year")
    desired_day = answer.get("desired_day")
    desired_month = answer.get("desired_month")
    desired_year = answer.get("desired_year")
    complete = answer.get("complete")
    print(f"calendar time answer: {answer}")
    if action:
        state = calendar_action_process(action=action, icon=icon, current_day=current_day, current_month=current_month, current_year=current_year, desired_day=desired_day, desired_month=desired_month, desired_year=desired_year, boxes_details=boxes_details, image2=image2, full_page_width=full_page_width, state=state)
    return state, complete

def calendar_action_process(boxes_details: list[dict], full_page_width: int, image2: bool, state: ApplicationState, action=None, icon=None, current_day=None, current_month=None, current_year=None, desired_day=None, desired_month=None, desired_year=None):
    page = state["current_page"]["page"]
    context = state.get("context")
    page_count = len(context.pages)
    if action == "click_month":
        current_box = boxes_details[icon]
        coordinates = current_box["bbox"]
        if image2:
            full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
            page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
        else:
            page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=740)
            page_x += 10
            page_y += 70
    if action == "white_pixel":
        current_answer = [action, -1]
        full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
        state = execute_action(current_answer=current_answer, current_box=-1, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    elif action == "click_month":
        years_apart = desired_year - current_year
        if years_apart != 0:
            if image2:
                for i in range(abs(years_apart)):
                    pyautogui.click(page_x, page_y)
            else:
                for i in range(abs(years_apart)):
                    page.mouse.click(page_x, page_y)
        else:
            if image2:
                pyautogui.click(page_x, page_y)
            else:
                page.mouse.click(page_x, page_y)
    elif action == "arrow_day":
        days_apart = day_calculator(current_day=current_day, current_month=current_month, current_year=current_year, desired_day=desired_day, desired_month=desired_month, desired_year=desired_year)
        if days_apart > 0:
            for i in range(days_apart):
                pyautogui.hotkey("right")
        elif days_apart < 0:
            for i in range(abs(days_apart)):
                pyautogui.hotkey("left")
    elif action == "arrow_month":
        total_click = (desired_year - current_year) * 12
        if total_click > 0:
            total_click += (desired_month - current_month)
        elif total_click == 0:
            total_click += abs(desired_month - current_month)
        else:
            total_click = abs(total_click)
            total_click += (current_month - desired_month)
        if image2:
            for i in range(total_click):
                page.mouse.click(page_x, page_y)
        else:  
            for i in range(total_click):
                pyautogui.click(page_x, page_y)
    elif action == "arrow_year":
        total_click = abs(desired_year - current_year)
        if image2:
            for i in range(total_click):
                page.mouse.click(page_x, page_y)
        else:
            for i in range(total_click):
                pyautogui.click(page_x, page_y)
            

    return state

def markdown_process(current_answer: dict, encoded_pyautogui_bytes1: str, old_bytes: str, body_text: str, page_x: float, page_y: float, state: ApplicationState, white_x=None, white_y=None):
    page = state["current_page"]["page"]

    for attempt in range(3):
        real_width, real_height = page_width_and_height_process(state=state)
        print(f"real width: {real_width}")
        pyautogui_width = real_width
        pyautogui_image2 = pyautogui.screenshot(region=(10, 40, real_width, 780))
        pyautogui_image2.show()
        pyautogui_buffer2 = io.BytesIO()
        pyautogui_image2.save(pyautogui_buffer2, format="PNG")
        pyautogui_bytes2 = pyautogui_buffer2.getvalue()
        encoded_pyautogui_bytes2 = base64.b64encode(pyautogui_bytes2).decode("utf-8")

        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)

        new_box = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            content = current_box["content"]
            new_box.append([icon, box_type, content])

        prompt = f"""
You're an AI Applicant Helper that is in the markup process.

Markdown definition: markdown - Used when clicking an element opens a list of selectable options, such as a dropdown, combobox, menu, or similar selection component. The markdown process is responsible for opening the element, discovering the available options, and selecting the correct option.

You're goal is to look at the the body text + the two images to find all the options for the question we are in and to choose what option we need to arrow down to.

current_question: {current_answer}
body_text: {body_text}

IMPORTANT:
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

Example to how you model your reasoning
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

Example output
{{
option_choice: 3,
current_option: 1
}}

Why we did that: The image shows we are on currently highlighted on option 1 and we need to go to option 3


Example to model your reasoning 2:
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

Example output 2
{{
option_choice: 3,
current_option: 0
}}


Why we did that: There is currently no highlighted option in the photo and we need to move to the third option
"""

        response = markdown_process_llm2.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_pyautogui_bytes2}"}}
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
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
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

def markdown_process(current_answer: list, ai_answers: list[list], state: ApplicationState, white_x=None, white_y=None):
    page = state["current_page"]["page"]
    context = state.get("context")
    page_count = len(context.pages)
    print(f"current answer: {current_answer}")
    current_question = current_answer[2]
    print(f"markdown current question: {current_question}")
    complete = False
    for attempt in range(5):
        encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
        pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 780))
        buffer = io.BytesIO()
        pyautogui_image.save(buffer, format="PNG")
        pyautogui_bytes = buffer.getvalue()
        pyautogui_encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
        data = {"image_input": pyautogui_encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
        response = requests.post("http://127.0.0.1:8000/image_process", json=data)
        response = response.json()
        pyautogui_encoded_bytes = response["encoded_bytes"]
        pyautogui_boxes_details = response["boxes_details"]
        pyautogui_encoded_bytes = boxes_only_process(encoded_bytes=pyautogui_encoded_bytes, boxes_details=pyautogui_boxes_details)

        body_text = page.locator("body").inner_text()
        page_elements = []

        text_elements = ""
        icon_elements = ""
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            bbox = current_box["bbox"]
            coordinates = [round(bbox[0], 2), round(bbox[1], 2), round(bbox[2], 2), round(bbox[3], 2)]
            content = current_box["content"]
            if box_type == "text":
                text_elements += f"{icon},{coordinates[0]},{coordinates[1]},{coordinates[2]},{coordinates[3]},{content}\n"
            else:
                icon_elements += f"{icon},{coordinates[0]},{coordinates[1]},{coordinates[2]},{coordinates[3]},{content}\n"
        print(f"markdown current question: {current_question}")
        prompt = f"""

You are an AI Applicant Helper handling ONLY the current job application question.



Use the visible page, body text, USER PROFILE, and common sense to determine the correct action.

Current Question: {current_question}

PAGE ELEMENTS FORMAT
[icon, coordinates, content]

Text elements: {text_elements}

Icon elements: {icon_elements}

Body Text: {body_text}

ACTIONS

1. arrow
Use for keyboard-selectable options/dropdowns.
- Find ALL available options from the image/page/body text.
- Identify the currently highlighted option.
- Choose the option that best matches the USER PROFILE.
- current_option = index of highlighted option.
- option_choice = index of desired option.

Format:
["arrow", current_option, option_choice]


2. fill
Use when a text field only needs text entered.

Format:
["fill", icon, text]


3. search
Use when typing text causes suggestions/options to appear.
Return all relevant text values that should be searched/entered.

Format:
["search", icon, current_question, list_of_text]


4. click
Use for a one-off click needed to complete ONLY the current question, such as selecting an option, continuing, or confirming.

Format:
["click", icon]


OUTPUT

Return ONE action using this structure:

{{
    "action": "arrow" | "fill" | "search" | "click",
    "icon": int | None,
    "text": str | None,
    "list_text": list[str] | None,
    "current_question": str | None,
    "current_option": int | None,
    "option_choice": int | None
}}

Examples:

Arrow:
{{
    "action": "arrow",
    "icon": None,
    "text": None,
    "list_text": None,
    "current_question": None,
    "current_option": 0,
    "option_choice": 4
}}

Fill:
{{
    "action": "fill",
    "icon": 10,
    "text": "Charlotte",
    "list_text": None,
    "current_question": None,
    "current_option": None,
    "option_choice": None
}}

Search:
{{
    "action": "search",
    "icon": 7,
    "text": None,
    "list_text": ["Python", "Playwright", "Java"],
    "current_question": {current_question},
    "current_option": None,
    "option_choice": None
}}

Click:
{{
    "action": "click",
    "icon": 3,
    "text": None,
    "list_text": None,
    "current_question": None,
    "current_option": None,
    "option_choice": None
}}


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
        if not complete:
            response = markdown_process_llm2.invoke([
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{pyautogui_encoded_bytes}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                    ]
                }
            ])
            details = response["raw"]
            

            new_tokens, model_name = details_process(details=details)
            state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
            answers = response["parsed"]
            print(f"markdown answers: {answers}")
            action = answers.get("action")
            icon = answers.get("icon")
            text = answers.get("text")
            list_text = answers.get("list_text")
            new_current_question = answers.get("current_question")
            current_option = answers.get("current_option")
            option_choice = answers.get("option_choice")
            if new_current_question:
                current_question = new_current_question
            if action == "arrow":
                current_answer = [action, current_option, option_choice]
            elif action == "fill":
                current_answer = [action, icon, text]
            elif action == "search":
                current_answer = [action, icon, current_question, list_text]
            else:
                current_answer = [action, icon]
            state = markdown_action(current_answer=current_answer, boxes_details=boxes_details, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
            state, complete, action = review_markdown_process(current_question=current_question, ai_answers=ai_answers, state=state)
        if complete:
            if action == "white_pixel":
                return state
            state, fully_complete = complete_markdown_process(current_question=current_question, ai_answers=ai_answers, state=state)
            if fully_complete:
                return state
    return state

def review_markdown_process(current_question: str, ai_answers: list[list], state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)
    page_elements = []
    text_elements = ""
    icon_elements = ""
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 2), round(bbox[1], 2), round(bbox[2], 2), round(bbox[3], 2)]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])
        if box_type == "text":
            text_elements += f"{icon},{coordinates[0]},{coordinates[1]},{coordinates[2]},{coordinates[3]},{content}\n"
        else:
            icon_elements += f"{icon},{coordinates[0]},{coordinates[1]},{coordinates[2]},{coordinates[3]},{content}\n"
    print(f"review markdown current question: {current_question}")
    prompt = f"""

You are an AI Applicant Helper in the Review Markdown Process.

Current Question: {current_question}

PAGE ELEMENTS FORMAT
[icon, coordinates, content]

text elements: {text_elements}

icon elements: {icon_elements}

All Answers: {ai_answers}

Decision Process

IMPORTANT
- Only look at the current question in your reasoning

1. First only look at the current question
2. If the question is answered correctly use the Escape Question Process
3. If the question is incorrect or not answered use the Finish Question Process

Finish Question Process
1. First determine if the options for the current question is open or not
2. If you see no options that means we need to reopen the box again.
   - Your responsibility is to find the icon that reopens the question
   - Example output: {{action: "click", icon: 8, complete: False}}


3. If you see options for the question, you will just mark the question as complete and make the action and icon None
   - Example: {{action: None, icon: None, complete: False}}

Escape Question Process
1. The first Step is to find all the questions in the image and list them
    - If we only see our current question then we will use the "exit" action
        - {{"action": "exit", "icon": whatever the exit icon is, complete: True}}
    - If we see all the questions in the image, then we will use the "white_pixel" action
        - {{"action": "white_pixel", "icon": -1, complete: True}}

Output Format"
action: str | None
icon: int | None
complete: bool

Example 1:
{{
action: "click",
icon: 12,
complete: False
reason:
I chose to click the current question again because the current question was not finished.
I chose to click the current question again because the answer was incorrect.
}}

Example 2:
{{
action: None,
icon: None,
complete: False
reason:
I chose to have no action because the option for the question is still open with no further action needing to be done.
}}


Example 3:
{{
action: "white_pixel",
icon: -1,
complete: True
reason:
I chose the white pixel because the question is answered correctly. We also see other questions in the image. Look at all answers to determine if other questions are in the image.
}}

Example 4:
{{
action: "exit",
icon: 9,
complete: True
reason:
I chose the exit action because the question is answered correctly but no other question is in the image, look at all answers for guidance.
}}


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
    response = review_markdown_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes2}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answers = response["parsed"]
    print(f"review markdown answers: {answers}")
    action = answers.get("action")
    icon = answers.get("icon")
    complete = answers.get("complete")
    if not action or not icon:
        return state, complete, action
    context = state.get("context")
    page_count = len(context.pages)
    current_answer = [action, icon]
    if icon >= 0:
        current_box = boxes_details[icon]
    else:
        current_box = -1
    state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    return state, complete, action



def complete_markdown_process(current_question: str, ai_answers: list[list], state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])
    prompt = f"""
Your an AI Applicant helper in the complete markdown process.

Your Task is to look at the instrucitons, images, all answers, and current question to help you through the complete markdown process.

You will only be looking at the current question and no other question.

current_question: {current_question}

All Answers: {ai_answers}

Instructions
1. First determine if we see options for the current question or if we only see our question in the images and not any other questions, look at the image and All Answers to determine that.
2. If we only see our question in the images, use the escape question process
3. If we see options for the current question that is not natural, which means options are overlapping other questions, and we need to get rid of them, use the escape question process
4. IF we see no other options for our question and see other questions in the image that means our question is complete and we don't need to use the escape question process.

Escape Question Process
1. Look at All Answers and determine if we only see our question on the images or do we see all questions.
2. If we only see our question on the images.
    - We need to find the exit icon to leave the question with the "exit" action.
    - Look for an icon that will allow us to leave the question.
    - Example output: {{action: "white_pixel", icon: -1, complete: True}}
3. If we see more questions besides for our own.
    - We use the "white_pixel" action to leave
    - the icon we will return for "white_pixel" will always be -1.
    - Example output: {{action: "exit", icon: 4, complete: True}}

ACTIONS
1. white_pixel - this will call a background pixel to leave the question, always call -1 for icon in white_pixel.
2. exit - this will click an icon on the page to leave the current question
For exit you need to be able to find the icon that will leave the current question so look at the images and NEW BOX to answer.

current_question: {current_question}

PAGE ELEMENTS FORMAT
[icon, type, coordinates, content]

Page Elements: {page_elements}

ITEMS FORMAT
[action, icon]
[str, int]

Example 1:
{{
action: "white_pixel"
icon: -1
complete: False
}}
Example 2:
{{
action: "exit"
icon: 8
complete: False
}}
Example 3:
{{
action: None
icon: None
complete: True
}}
"""
    response = complete_markdown_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes2}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    print(f"complete search answer: {answer}")
    action = answer.get("action")
    icon = answer.get("icon")
    complete = answer.get("complete")
    if action:
        if icon and icon >= 0:
            current_box = boxes_details[icon]
        else:
            current_box = -1
        context = state.get("context")
        page_count = len(context.pages)
        current_answer = [action, icon]


        state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    return state, complete

def markdown_action(current_answer: list, boxes_details: list[dict], full_page_width: int, full_page_height: int, page_count: int, state: ApplicationState):
    print(f"current markdown answer: {current_answer}")
    action = current_answer[0]
    icon = current_answer[1]
    current_box = boxes_details[icon]
    state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    return state

def search_process(all_text: list[str], current_question: str, ai_answers: list[list], state: ApplicationState, process=None):
    page = state["current_page"]["page"]
    context = state.get("context")
    page_count = len(context.pages)
    complete = False
    current_text = all_text[0]
    print(f"answers: {all_text}")
    for attempt in range(6):
        pyautogui.hotkey("enter")
        time.sleep(4)
        pyautogui.hotkey("down")
        encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
        pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 780))
        buffer = io.BytesIO()
        pyautogui_image.save(buffer, format="PNG")
        pyautogui_bytes = buffer.getvalue()
        pyautogui_encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
        data = {"image_input": pyautogui_encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
        response = requests.post("http://127.0.0.1:8000/image_process", json=data)
        response = response.json()
        pyautogui_encoded_bytes = response["encoded_bytes"]
        pyautogui_boxes_details = response["boxes_details"]
        pyautogui_encoded_bytes = boxes_only_process(encoded_bytes=pyautogui_encoded_bytes, boxes_details=pyautogui_boxes_details)
        prompt = f"""
Your an AI applicant helper whose job is to help us out in the search process.
We have just entered some text and your job is to tell us one of a few things. 
Only look at the current question and ignore the rest, our job is to only answer the current question.
current_question: {current_question}

Go through the Search Question Process to answer the question.

Search Question Process
1. Your First step is to find the current question in the images
2. Determine if there are options available for the question in one of the images
    - If no options are available for the question, then return {{"action": None, current_option: None, option_choice: None}}
3. If the options are available go through this process
    - First find the highlighted option to determine our current option
    - Use the User Profile to answer the question, find the option that best fits the answer
    - If no option fits the answer you determined, then return {{"action": None, current_option: None, option_choice: None}}
    - If there is an option that fits your answer then return {{"action": arrow, current_option: whatever the highlighted option is, option_choice: whatever the option number you choose}}

arrow - this means we need to move the arrow keys up or down to be able to click a suggestion for the skill or search item

Within this process you will be tasked to review if we need to arrow down/up to enter an icon.

If there are no options available just mark Items as None
items: None

Output Style
action: str | None
current_option: int | None
option_choice: int | None


Example 1
{{
action: "arrow"
current_option: 4
option_choice: 6
}}

Example 2
{{
action: "arrow"
current_option: 0
option_choice: 6
}}

Example 3
{{
action: None
current_option: None
option_choice: None
}}

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
        if not complete:
            response = search_process_llm2.invoke([
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{pyautogui_encoded_bytes}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                    ]
                }
            ])
            details = response["raw"]
            new_tokens, model_name = details_process(details=details)
            state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
            answers = response["parsed"]
            print(f"search answers: {answers}")
            action = answers.get("action")
            option_inputted = False
            if action:
                option_inputted = True
                current_option = answers.get("current_option")
                option_choice = answers.get("option_choice")
                current_answer = [action, current_option, option_choice]
                state = search_action(current_answer=current_answer, state=state)
            print(f"option inputted: {option_inputted}")
            state, complete, next_text, action = review_search_process(all_text=all_text, current_text=current_text, current_question=current_question, ai_answers=ai_answers, option_inputted=option_inputted, state=state)
            current_text = next_text
        if complete:
            if process or action == "white_pixel":
                return state
            state, fully_complete = complete_search_process(current_question=current_question, ai_answers=ai_answers, state=state)
            if fully_complete:
                return state
    return state


def review_search_process(current_question: str, all_text: list[str], current_text: str, ai_answers: list[list], option_inputted: bool, state: ApplicationState, process=None):
    page = state["current_page"]["page"]
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)
    page_elements = []
    text_elements = ""
    icon_elements = ""
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 2), round(bbox[1], 2), round(bbox[2], 2), round(bbox[3], 2)]
        content = current_box["content"]
        if box_type == "text":
            text_elements += f"{icon},{coordinates[0]},{coordinates[1]},{coordinates[2]},{coordinates[3]},{content}\n"
        else:
            icon_elements += f"{icon},{coordinates[0]},{coordinates[1]},{coordinates[2]},{coordinates[3]},{content}\n"
        page_elements.append([icon, box_type, coordinates, content])
    print(f"review search process current question: {current_question}")
    prompt = f"""


You are an AI Applicant Helper handling ONLY the current question.

Current Question: {current_question}
All Text: {all_text}
Current Text: {current_text}

PAGE ELEMENTS
[icon, coordinates, content]

Text elements: {text_elements}

Icon Elements: {icon_elements}

AI Answers: {ai_answers}

Option Inputted: {option_inputted}

RULES

If Current Text is NOT the last item in All Text:
- Find the current question's text-input icon.
- Return "click" and the NEXT item from All Text.

If option inputted is False, here is option_inputted: {option_inputted} and we are on the last item of all text with no answer to the question so far then do this.
- Find the current question's text-input icon.
- Look at the Current Text and try searching a different text for the current text, use the User Profile as help.

If Current Text IS the last item of the all text:
- Other questions visible in AI Answers → "white_pixel", icon -1.
- Only current question visible in AI Answers → "exit" using its exit icon.

If option inputted is False and we are on the last item of all text with no answer to the question so far then do this.
{{
"action": "click",
"icon": 12
"reason": option inputted is false, there is no answered question, and we are on the last option in all text
next_text: A different variation of current text, use User Profile as help
}}

OUTPUT
{{
"action": "click" | "white_pixel" | "exit",
"icon": int,
"reason": str,
"next_text": str | None
}}

USER PROFILE
email={state["email"]}
password={state["password"]}
name={state["first_name"]} {state["last_name"]}
phone={state["phone_number"]}
address={state["address_line1"]} {state["address_line2"]}, {state["city"]}, {state["user_state"]} {state["zip_code"]}, {state["country"]}
date={state["date"]}
work_authorized={state["work_authorized"]}
requires_sponsorship={state["requires_sponsorship"]}
veteran={state["veteran"]}
disability={state["disability"]}
linkedin={state["linkedin_url"]}
github={state["github_url"]}
portfolio={state["portfolio_url"]}
work_experience={state["work_experience"]}
education={state["education"]}
resume={state["resume_text"]}
cover_letter={state["cover_letter_text"]}

Job source: prefer Other, Job Board, Website, or closest equivalent.
"""
    prompt = f"""
You're an AI Applicant Helper and you will only be looking at the current question, images, and Boxes to help decide your answer.

current_question: {current_question}

all_text: {all_text}

current_text: {current_text}

PAGE ELEMENTS FORMAT
[icon, coordinates, content]

Text Elements: {text_elements}

Icon Elements: {icon_elements}

You have 3 options:

All Answers: {ai_answers}

Process for deciding output
1. First look at the current question and see if we are on the last input of {all_text}
2. If we are not on the last input of {all_text}
    - we need to find the text icon of the current question to continue inputting our next text.
3. If we are on the last input then we use the Escape Question Process.

Escape Question Process
1. Look at All Answers and determine if we only see our question on the images or do we see all questions.
2. If we only see our question on the images.
    - We need to find the exit icon to leave the question with the "exit" action.
    - Look for an icon that will allow us to leave the question.
    - Example output: {{action: "white_pixel", icon: -1, complete: True}}
3. If we see more questions besides for our own.
    - We use the "white_pixel" action to leave
    - the icon we will return for "white_pixel" will always be -1.
    - Example output: {{action: "exit", icon: 4, complete: True}}

Actions
1. click - we only use this to click the icon to enter text, if we have no more text to enter do no call this.
2. white_pixel - we only use this if we have inputted the last text and there are more questions that show up on the images.
3. exit - we use the exit action when we have inputted the last text and there is only the {current_question} on the images with no other questions present so we need to find the exit icon.

Example Output Format:

["Action", icon, "reason"]
[str, int, str]

Next text should be the next item in the all text list


Example 1:

{{
action: "click"
icon: 4
reason: "We need to click icon 4 to allow us to input the next text"
next_text: "whatever the next input is on the lists"
}}


Example 2:
action: "white_pixel"
icon: -1
reason: "We have inputted every text and there are other questions present which means we use the white pixel"
next_text: None

Example 3:

action: "exit"
icon: 8
reason: "We have inputted the last text in {all_text} and there is only the current question in the image which means we need to find and click the exit icon
next_text: None

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
    prompt = f"""
You are an AI Applicant Helper handling ONLY the current question.

Current Question: {current_question}
All Text: {all_text}
Current Text: {current_text}
All Answers: {ai_answers}

PAGE ELEMENTS
[icon, type, coordinates, content]

{page_elements}

RULES

If Current Text is NOT the last item in All Text:
- Find the current question's text-input icon.
- Return "click" and the NEXT item from All Text.


If Current Text IS the last item:
- Other questions visible → "white_pixel", icon -1.
- Only current question visible → "exit" using its exit icon.

OUTPUT
{{
"action": "click" | "white_pixel" | "exit",
"icon": int,
"reason": str,
"next_text": str | None
}}

USER PROFILE
email={state["email"]}
password={state["password"]}
name={state["first_name"]} {state["last_name"]}
phone={state["phone_number"]}
address={state["address_line1"]} {state["address_line2"]}, {state["city"]}, {state["user_state"]} {state["zip_code"]}, {state["country"]}
date={state["date"]}
work_authorized={state["work_authorized"]}
requires_sponsorship={state["requires_sponsorship"]}
veteran={state["veteran"]}
disability={state["disability"]}
linkedin={state["linkedin_url"]}
github={state["github_url"]}
portfolio={state["portfolio_url"]}
work_experience={state["work_experience"]}
education={state["education"]}
resume={state["resume_text"]}
cover_letter={state["cover_letter_text"]}

Job source: prefer Other, Job Board, Website, or closest equivalent.
"""
    response = review_search_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes2}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    print(f"review search answers: {answer}")
    action = answer.get("action")
    icon = answer.get("icon")
    print(f"action: {action}")
    print(f"icon: {icon}")
    next_text = answer.get("next_text")
    current_answer = [action, icon]
    complete = False
    if icon != None and icon >= 0:
        current_box = boxes_details[icon]
    else:
        current_box = -1
    if action != "click":
        complete = True
        if process:
            return state, complete, next_text, action
        context = state.get("context")
        page_count = len(context.pages)
        state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    else:
        coordinates = current_box["bbox"]
        page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
        page.mouse.click(page_x, page_y)
        for i in range(500):
            page.keyboard.press("Backspace")
        page.keyboard.type(next_text)
        page.keyboard.press("Enter")
        time.sleep(4)
    return state, complete, next_text, action

def exit_question_process(current_quesstion: str, ai_answers: list[list], state: ApplicationState, all_text=None, process=None):
    page = state["current_page"]["page"]
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])
    print(f"current question: {current_question}")
    print(f"all text: {all_text}")
    print(f"page elements: {page_elements}")
    prompt = f"""
You are an AI Applicant Helper handling ONLY the current question.

Current Question: {current_question}
All Text: {all_text}

PAGE ELEMENTS
[icon, type, coordinates, content]

RULES

If Current Text is NOT the last item in All Text:
- Find the current question's text-input icon.
- Return "click" and the NEXT item from All Text.

If Current Text IS the last item:
- Other questions visible → "white_pixel", icon -1.
- Only current question visible → "exit" using its exit icon.

OUTPUT
{{
"action": "click" | "white_pixel" | "exit",
"icon": int,
"reason": str,
"next_text": str | None
}}

USER PROFILE
email={state["email"]}
password={state["password"]}
name={state["first_name"]} {state["last_name"]}
phone={state["phone_number"]}
address={state["address_line1"]} {state["address_line2"]}, {state["city"]}, {state["user_state"]} {state["zip_code"]}, {state["country"]}
date={state["date"]}
work_authorized={state["work_authorized"]}
requires_sponsorship={state["requires_sponsorship"]}
veteran={state["veteran"]}
disability={state["disability"]}
linkedin={state["linkedin_url"]}
github={state["github_url"]}
portfolio={state["portfolio_url"]}
work_experience={state["work_experience"]}
education={state["education"]}
resume={state["resume_text"]}
cover_letter={state["cover_letter_text"]}

Job source: prefer Other, Job Board, Website, or closest equivalent.
"""
    response = review_search_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes2}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    print(f"review search answers: {answer}")
    action = answer.get("action")
    icon = answer.get("icon")
    print(f"action: {action}")
    print(f"icon: {icon}")
    next_text = answer.get("next_text")

def complete_search_process(current_question: str, ai_answers: list[list], state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])
    prompt = f"""
Your an AI Applicant helper in the complete search process.

We have entered all the text in the search process.

We will only be looking at the current question

current_question: {current_question}

All Answers: {ai_answers}

IMPORTANT
1. First determine if we see options for the current question or if we only see our question in the images and not any other questions, look at the image and All Answers to determine that.
2. If we only see our question in the images, use the escape question process
3. If we see options for the current question that is not natural, which means options are overlapping other questions, and we need to get rid of them, use the escape question process
4. IF we see no other options for our question and see other questions in the image that means our question is complete and we don't need to use the escape question process.

All Answers: {ai_answers}

current_question: {current_question}

Escape Question Process
1. Look at All Answers and determine if we only see our question on the images or do we see all questions.
2. If we only see our question on the images.
    - We need to find the exit icon to leave the question with the "exit" action.
    - Look for an icon that will allow us to leave the question.
    - Example output: {{action: "white_pixel", icon: -1, complete: True}}
3. If we see more questions besides for our own.
    - We use the "white_pixel" action to leave
    - the icon we will return for "white_pixel" will always be -1.
    - Example output: {{action: "exit", icon: 4, complete: True}}

ACTIONS
1. white_pixel - this will call a background pixel to leave the question, always call -1 for icon in white_pixel.
2. exit - this will click an icon on the page to leave the current question
For exit you need to be able to find the icon that will leave the current question so look at the images and NEW BOX to answer.

PAGE ELEMENTS FORMAT
[icon, type, coordinates, content]

Page Elements: {page_elements}

ITEMS FORMAT
[action, icon]
[str, int]

Example 1:
{{
action: "white_pixel"
icon: -1
complete: False
}}
Example 2:
{{
action: "exit"
icon: 8
complete: False
}}
Example 3:
{{
action: None
icon: None
complete: True
}}
"""
    response = complete_search_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes2}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    print(f"complete search answer: {answer}")
    action = answer.get("action")
    icon = answer.get("icon")
    complete = answer.get("complete")
    if action:
        if icon and icon >= 0:
            current_box = boxes_details[icon]
        else:
            current_box = -1
        context = state.get("context")
        page_count = len(context.pages)
        current_answer = [action, icon]


        state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    return state, complete

def search_action(current_answer: list, state: ApplicationState):
    print(f"search action answer: {current_answer}")
    action = current_answer[0]
    if action == "arrow":
        print(f"going through search action")
        option_choice = current_answer[1]
        current_option = current_answer[2]
        option_difference = option_choice - current_option
        if option_difference == 0:
            pyautogui.hotkey("up")
            pyautogui.hotkey("down")
            pyautogui.hotkey("enter")
        elif option_difference > 0:
            for i in range(option_difference):
                pyautogui.hotkey("down")
            pyautogui.hotkey("enter")
        else:
            for i in range(abs(option_difference)):
                pyautogui.hotkey("up")
            pyautogui.hotkey("enter")
    return state


def click_and_view_process(state: ApplicationState):
    page = state["current_page"]["page"]
    context = state.get("context")
    page_count = len(context.pages)

    for attempt in range(5):
        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
        encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)

        encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
        encoded_bytes2 = boxes_only_process(encoded_bytes=encoded_bytes2, boxes_details=boxes_details)

        # Convert the OmniParser results into the smaller format
        # that will be sent to the AI.
        page_elements = []

        for current_box in boxes_details:
            bbox = current_box["bbox"]
            coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4),]
            page_elements.append([current_box["icon"], current_box["type"], coordinates, current_box["content"]])

        coordinates = []

        for current_box in boxes_details:
            coordinates.append(current_box["bbox"])

        white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)

        prompt = f"""
You are an AI job-application assistant completing fields revealed by an
"Add more" or "Add another" option.

GOAL
- Correctly answer every relevant visible question.
- Fix visible validation errors.
- Leave already-correct answers unchanged.
- Use the user's profile as the primary source of truth.
- Use reasonable inference when the profile does not directly provide an answer.
- Complete all currently visible fields before clicking an "Add more" option.
- Return an action for every visible field that needs an action.
- Use the input or option icon instead of the question-label icon.
- Do not submit or advance the overall application.

HOW THIS PROCESS WORKS
- Never pick the icon that is used to submit or to save and continue, that is for another process.
- Its final action can be click_and_view when an "Add more" option should
  reveal another group of questions.
- If no "Add more" option should be clicked, do not return click_and_view.
- Returning no click_and_view action tells the controller that this process
  is complete.
- Do not return a submit action

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
add_more: add another option will add more items for examples like add more education, add more experience, things of that nature


Page Elements format
[icon, type, coordinates, content]

PAGE ELEMENTS
{page_elements}

ITEMS ELEMENTS

ACTIONS
skip: [action]

fill: [action, icon, action_text]

fill_with_time: [action, icon, action_text]

delete: [action, icon]

delete_and_fill: [action, icon, action_text]

click: [action, icon]

upload_resume: [action, icon]

upload_cover_letter: [action, icon]

markdown: [action, icon, current_question]

add_more: [action, icon, submit_text]


Example:

items: [["skip"], ["fill", 28, {state["email"]}], ["fill_with_time", 35, "08/01/2020"], ["delete", 38], ["delete_and_fill", 42, {state["first_name"]}], ["click", 32], ["upload_resume", 50], ["upload_cover_letter", 52], ["markdown", 60, "What U.S. State are you in?"], ["add_more", 30]]

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

        response = question_process_llm2.invoke(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}},
                        {"type": "image_url","image_url": {"url": f"data:image/png;base64,{encoded_bytes2}"}},
                    ],
                }
            ]
        )

        details = response["raw"]
        print(f"Click and view details: {details}")

        new_tokens, model_name = details_process(details=details)

        state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)

        total_cost = state["token_usage"]["total_cost"]

        if total_cost > 0.10:
            state["action"] = "exit"
            state["leaving_reason"] = (
                "The cost exceeded $0.10 during the click-and-view "
                f"process. Total cost: ${total_cost}"
            )
            return state

        answers = response["parsed"]
        ai_answers = answers["items"]

        print(f"Click and view AI answers: {ai_answers}")

        add_more = False
        for i in range(len(ai_answers)):
            current_answer = ai_answers[i]
            action = current_answer[0] if len(current_answer) > 0 else None
            if action == "add_more":
                add_more = True

        if not add_more:
            state = action_process(ai_answers=ai_answers, boxes_details=boxes_details, state=state, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, white_x=white_x, white_y=white_y)
            return state

        state = action_process(ai_answers=ai_answers, boxes_details=boxes_details, state=state, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, white_x=white_x, white_y=white_y)


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
Developed automation tools using Python, Playwright, and SQL.

I am legally authorized to work in America.
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
        pyautogui.moveTo(0, 0)
        final_state = mapping.invoke({"url": url2, "current_page": current_page, "token_usage": token_usage, "browser": browser, "context": context, "user_id": user_id})
        print(f"final_state: {final_state}")
        leaving_reason = final_state.get("leaving_reason")
        print(f"Browser closing due to : {leaving_reason}")
        browser.close()

complete_application(url)

print("hello world")