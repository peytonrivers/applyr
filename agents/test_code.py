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
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision

from langchain_openai import ChatOpenAI

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
find_cookies_llm = llm.with_structured_output(FindCookies, include_raw=True)

url = "https://www.allstate.jobs/job/23310874/software-engineer-product-security/"


def screenshot_page(page):
    screenshot_bytes = page.screenshot(full_page=True)
    screenshot_ascii = base64.b64encode(screenshot_bytes).decode("utf-8")
    return screenshot_ascii

with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    screenshot_page = screenshot_page(page)
    body_text = page.locator("body").inner_text() or ""
    buttons = page.locator("button")
    button_elements = []
    for i in range(buttons.count()):
        button_elements.append({"button": buttons.nth(i), "index": i})
    links = page.locator("a")
    link_elements = []
    for i in range(links.count()):
        link_elements.append({"link": links.nth(i), "index": i})

    prompt = """Your an AI Applicant Helper and your job is to determine what type of page this is,
    here are your options: Apply, Cookies, Signup, Forms, Verification, Error
    If your options are Apply or Cookies: your job is to give the exact text and nothing else of the element we are going to be clicking
    Ex: Accept, Apply Now, Save and Continue, Apply Manually, Continue
    It needs to be the exact text and nothing else!!!
    """
    response = find_cookies_llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"You need to find a the button index or link index or neither that will accept the cookies, if the option to click is not link please enter None for link_index, if the option to click is not button please enter None for button_index, if both are wrong please enter none for both link_index and button_index, button: {button_elements}, links: {link_elements}"},
            ]
        }
    ])
    raw = response["raw"]
    decision = response["parsed"]
    print(decision)
    usage = raw.response_metadata.get("token_usage", {})
    print("\nDECIDE PAGE TOKEN USAGE")
    print(f"Prompt tokens: {usage.get('prompt_tokens')}")
    print(f"Completion tokens: {usage.get('completion_tokens')}")
    print(f"Total tokens: {usage.get('total_tokens')}")
    print(response)
    browser.close()

