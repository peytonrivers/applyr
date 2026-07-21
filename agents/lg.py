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
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

from langchain_openai import ChatOpenAI



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

url = "https://www.allstate.jobs/job/23538686/software-engineer-all-levels-/"

print(url.title)