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
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess, AITokens
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END

graph = StateGraph(ApplicationState)


import time
import os
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_KEY")
MODEL_NAME = "gpt-5.4-mini"
llm = ChatOpenAI(model=MODEL_NAME, temperature = 0.3, api_key=openai_key)
structured_llm = llm.with_structured_output(ClickAction, include_raw=True)
multiple_question_llm = llm.with_structured_output(MultipleQuestion, include_raw=True)
all_elements_llm = llm.with_structured_output(AllElements, include_raw=True)
new_cookies_process_llm = llm.with_structured_output(NewCookiesProcess, include_raw=True)
cookies_process_llm = llm.with_structured_output(CookiesProcess, include_raw=True)
decide_page_llm = llm.with_structured_output(DecidePage, include_raw=True)
apply_process_llm = llm.with_structured_output(ApplyProcess, include_raw=True)
signup_process_llm = llm.with_structured_output(SignupProcess, include_raw=True)
forms_action_llm = llm.with_structured_output(FormsAction, include_raw=True)

url = "https://www.allstate.jobs/job/23556274/ai-software-engineer/"
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
    print(f"Cached tokens: {cached_tokens}")
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
    full_page_width = 1280
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    page.set_viewport_size({"width": full_page_width, "height": full_page_height})
    screenshot = page.screenshot()
    encoded_bytes = base64.b64encode(screenshot).decode("utf-8")
    return encoded_bytes

def omniparser_process(state: ApplicationState):
    encoded_bytes = screenshot_process(state)
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("https://omniparser.apply-r.com", json=data)
    response_data = response.json()


def decide_page(state: ApplicationState):
    encoded_bytes = screenshot_process(state)
    prompt = """Your an AI Application Helper and your job is to decide what page this is
    1. Cookies - You always choose this page if there are cookies on the page
    2. Application - You choose this page if we need to click apply now, apply manually, or we only need to click one buttton to continue
    3. Signup - You choose this page if we need to signup or login or create an account for the user.
    4. Forms - You choose this page if there is forms that need to be filled
    5. Verification - You choose this page if there is a verification code that needs to be filled out.
    6. Error - You choose this page if there is an error or the page doesn't exist.
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
    return state

def decide_routing(state: ApplicationState):
    action = state["action"]
    
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
    encoded_bytes = screenshot_process(state)
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("https://omniparser.apply-r.com/image_process", json=data)
    response_data = response.json()
    new_bytes = response_data["image"]
    decoded_new_bytes = base64.b64decode(new_bytes.encode("utf-8"))
    boxes_details = response_data["bounding_boxes"]
    prompt = f"""
Your an AI Applicant Helper and your Job is to pick the icon that will allow you to accept/continue/yes with the cookies.
Boxes Details: {str(boxes_details)}
Ex:
    follow_through_index: 37
    follow_through_reason: This is because the text said yes with the image showcasing that clicking this element would accept the cookies
"""
    ai_response = cookies_process_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{new_bytes}"}}
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
        new_page = new_page.value
        time.sleep(5)
    except Exception:
        page.wait_for_load_state("domcontentloaded")
        time.sleep(5)
    screenshot = page.screenshot()
    buffer = io.BytesIO(screenshot)
    image = Image.open(buffer)
    image.show()
    time.sleep(3)
    return state


def apply_process(state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes = screenshot_process(state)
    prompt = """
Your an AI Applicant Helper and your job is to look for the button that with start/continue the application process.
Usually these buttons contain text like this: 'apply now', 'apply manually', 'apply', 'start application', 'continue application'.
Always choose to apply manually if the option is there.
"""
    response = apply_process_llm.invoke([
        {"role": "user",
         "content": [
             {"type": "text", "text": prompt},
             {"type": "image", "image": {"url": f"data:image/png;base64,{encoded_bytes}"}}
         ]
         }
    ])
    details = response["raw"]
    decision = response["parsed"]
    new_tokens = details.usage_metadata
    state = ai_token_tracker(new_tokens=new_tokens, state=state)
    icon = decision["icon"]
    icon_reason = decision["icon_reason"]
    
def apply_action(icon: str, state: ApplicationState):
    print("hello")

with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    print(page.title)
    time.sleep(3)
    screenshot = page.screenshot()
    encoded_bytes = base64.b64encode(screenshot).decode("utf-8")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("https://omniparser.apply-r.com/image_process",json=data)
    response_data = response.json()
    new_bytes = response_data["image"]
    decoded_new_bytes = base64.b64decode(new_bytes.encode("utf-8"))
    buffer_bytes = io.BytesIO(decoded_new_bytes)
    new_image = Image.open(buffer_bytes)
    new_image.show()
    print(response_data["bounding_boxes"])


graph = StateGraph(ApplicationState)

graph.add_node("decide_page", decide_page)
graph.add_node("cookies_process", cookies_process)
graph.add_node("decide_routing", decide_routing)

graph.add_edge(START, "decide_page")
graph.add_conditional_edges("decide_page", decide_routing, {"cookies": "cookies_process", "error": END})
graph.add_edge("cookies_process", END)

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