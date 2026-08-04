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

class FindCookies(TypedDict):
    link_index: int | None
    button_index: int | None
    reason: str

openai_key = os.getenv("OPENAI_KEY")
llm = ChatOpenAI(model="gpt-5-nano", temperature = 0.3, api_key=openai_key)
structured_llm = llm.with_structured_output(ClickAction)
multiple_question_llm = llm.with_structured_output(MultipleQuestion)
all_elements_llm = llm.with_structured_output(AllElements)
cookies_process_llm = llm.with_structured_output(CookiesProcess)
decide_page_llm = llm.with_structured_output(DecidePage, include_raw=True)
apply_process_llm = llm.with_structured_output(ApplyProcess)
signup_process_llm = llm.with_structured_output(SignupProcess)
forms_action_llm = llm.with_structured_output(FormsAction)
question_process_llm = llm.with_structured_output(QuestionProcess, include_raw=True)




url = "https://www.allstate.jobs/job/23556274/ai-software-engineer/"

input_cost = 0.20 / 1000000
output_cost = 1.20 / 1000000
cached_cost = 0.02 / 1000000
    

def screenshot_page(page):
    screenshot_bytes = page.screenshot(full_page=True)
    screenshot_ascii = base64.b64encode(screenshot_bytes).decode("utf-8")
    return screenshot_ascii

file_path = "/Users/peytonrivers/Desktop/small5.png"
img = Image.open(file_path)
buffer = io.BytesIO()
image = img.save(buffer, format="PNG")
byt = buffer.getvalue()
encoded_bytes = base64.b64encode(byt).decode("utf-8")
data = {"image_input": encoded_bytes, "box_threshold": 0.02, "iou_threshold": 0.05, "use_paddleocr": True, "imgsz": 900}
data = requests.post("http://127.0.0.1:8000/image_process", json=data)
data = data.json()
data_bytes = data["encoded_bytes"]
boxes_details = data["boxes_details"]
data_decoded = base64.b64decode(data_bytes.encode("utf-8"))
buffer_data = io.BytesIO(data_decoded)
img = Image.open(buffer_data)
img.show()
time.sleep(5)

prompt = f"""
Find the icon for to be able to apply for this application:
boxes details: {boxes_details}
"""

response = apply_process_llm.invoke([
    {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
        ]
    }
])

print(response)