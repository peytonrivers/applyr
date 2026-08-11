import asyncio
from playwright.async_api import async_playwright, Playwright
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from playwright.sync_api import TimeoutError
from typing import TypedDict
import random
import json
import time
import base64
import io
import requests
from PIL import Image
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, QuestionProcess

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama


import time
import os
from dotenv import load_dotenv
load_dotenv()

url = "https://practice.expandtesting.com/dropdown"



ollama_llm = ChatOllama(model="qwen3.5:9b", temperature=0.1)

response = ollama_llm.invoke("Who was the first president of the united states?")
print(response)

"""with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    full_page_width = 1280
    full_page_height = page.evaluate() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); })
    page.set_viewport_size({"width": full_page_width, "height": full_page_height})
    encoded_bytes = base64.b64encode((page.screenshot())).decode("utf-8")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    response_data = response.json()
    encoded_bytes = response_data["encoded_bytes"]
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image.show()
    time.sleep(5)"""

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
3. click - when you want to click/unclick an element
4. delete - used when want to delete the given text
5. delete and fill - used when you want to delete the given text and then fill it out with new info

Process Action Section
6. upload resume - used when you need to upload a resume
7. upload cover letter - used when you need to upload a cover letter
8. click and view - used when
9. scroll - when you are at a markdown element and want to see more options
10. submit - the submit/save and continue/continue button on a page

Look at the boxes details and the image to help you determine which icon we are looking at

Ex 1:
{{
action: skip,
reason: This question has already been filled out
}}

Ex 2:
{{
action: fill,
action_text: johndoe@gmail.com,
icon: 28,
reason: This question tells us to fill out the user's email
}}

Ex 3:
{{
action: click,
icon: 32,
reason: We need to click yes he is a U.S. citizen
}}

Ex 4:
{{
action: delete,
icon 38,
reason: This is an input that is not correct as well as not required
}}

Ex 5:
{{
action: delete and fill,
action_text: John,
icon 42,
reason: This input that shows his first name is not correct and I am inputting the user John
}}

Ex 6:
{{
action: upload resume,
icon: 50,
reason: the question says we need to upload a resume
}}

Ex 7:
{{
action: upload cover letter,
icon: 52
reason: the question says we need to upload a cover letter
}}

Ex 8:
{{
action: scroll,
icon: 60,
question: What U.S. State are you in?,
reason: we are currently in a dropdown question asking what U.S. state the user is in with more options that can be scrolled to find.
}}

Ex 9:
{{
action: click and view,
icon: 22,
Question: Add More work Experience,
reason: We need to add more work experience for the user
}}

Ex 10:
{{
action: submit,
icon: 30,
reason: This is the submit/save and continue button on the page
}}
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
    state = action_process(ai_answers=ai_answers, boxes_details=boxes_details, state=state)
    return state

def action_process(ai_answers: list[dict], boxes_details: list[dict], state: ApplicationState):
    ai_answers.sort(key=lambda x: {"skip": 0,"fill": 1,"delete": 2, "delete and fill": 3, "click": 4, "upload resume": 5, "upload cover letter": 6, "scroll": 7, "click and view": 8, "submit": 9}.get(x["action"].lower(), 999))
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
        page.keyboard.type(action_text)
    if action == "click":
        page.mouse.click(page_x, page_y)

