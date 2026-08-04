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