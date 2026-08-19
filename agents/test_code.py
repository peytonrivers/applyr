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
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, QuestionProcess, MarkdownProcess

from langchain_openai import ChatOpenAI


import cv2
import numpy as np
import pyautogui
import time
import os
from dotenv import load_dotenv
load_dotenv()

class FindCookies(TypedDict):
    link_index: int | None
    button_index: int | None
    reason: str

openai_key = os.getenv("OPENAI_KEY")
llm = ChatOpenAI(model="gpt-5.6-luna", temperature = 0.3, api_key=openai_key)
structured_llm = llm.with_structured_output(ClickAction)
multiple_question_llm = llm.with_structured_output(MultipleQuestion)
all_elements_llm = llm.with_structured_output(AllElements)
cookies_process_llm = llm.with_structured_output(CookiesProcess)
decide_page_llm = llm.with_structured_output(DecidePage, include_raw=True)
apply_process_llm = llm.with_structured_output(ApplyProcess)
signup_process_llm = llm.with_structured_output(SignupProcess)
forms_action_llm = llm.with_structured_output(FormsAction)
question_process_llm = llm.with_structured_output(QuestionProcess, include_raw=True)




url = "https://cloudfront.careeronestop.org/JusticeImpacted/Toolkit/practice-job-application-form.aspx?practice-job-application-form.aspx="
# url = "https://demoqa.com/select-menu?utm_source=chatgpt.com"

input_cost = 0.20 / 1000000
output_cost = 1.20 / 1000000
cached_cost = 0.02 / 1000000
    

def empty_pixel_process(encoded_bytes: str, coordinates: list[list]):
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    format = image.format
    if format != "PNG":
        image.save("my_screenshot.png")
    image_width, image_height = image.size
    print(f"image width: {image_width}")
    print(f"image height: {image_height}")
    np_image = np.array(image)
    cv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    black = (0, 0, 0)
    for i in range(len(coordinates)):
        coordinate = coordinates[i]
        x1 = round(coordinate[0] * image_width)
        print(f"x1: {x1}")
        y1 = round(coordinate[1] * image_height)
        print(f"y1: {y1}")
        x2 = round(coordinate[2] * image_width)
        print(f"x2: {x2}")
        y2 = round(coordinate[3] * image_height)
        print(f"y2: {y2}")
        height_diff = y2 - y1
        print(f"height diff: {height_diff}")
        for l in range(height_diff):
            cv_image = cv2.line(cv_image, (x1, y1), (x2, y1), black, 3)
            y1 += 1
    cv2.imshow('Window Title', cv_image)

    # 3. Wait infinitely until any key is pressed
    cv2.waitKey(0)

    # 4. Clean up and close the window safely
    cv2.destroyAllWindows()

file_path = "/Users/peytonrivers/Desktop/small7.png"
img = Image.open(file_path)
buffer = io.BytesIO()
image = img.save(buffer, format="PNG")
byt = buffer.getvalue()
encoded_bytes = base64.b64encode(byt).decode("utf-8")
data = {"image_input": encoded_bytes, "box_threshold": 0.02, "iou_threshold": 0.05, "use_paddleocr": True, "imgsz": 900}
data = requests.post("http://127.0.0.1:8000/image_process", json=data)
data = data.json()
encoded_bytes = data["encoded_bytes"]
boxes_details = data["boxes_details"]
coordinates = []
for i in range(len(boxes_details)):
    current_box = boxes_details[i]
    coordinate = current_box["bbox"]
    coordinates.append(coordinate)
empty_pixel_process(encoded_bytes, coordinates)





def markup_process(current_question: str, body_text: str):
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

USER PROFILE
User is from: Arkansas
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
    response = llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])


    print(response.content)


body_text = f"""
`\n\n\n  \n    \n      \n        \n          \n            \n          \n        \n        ApplyR\n      \n\n      \n        Home\n      \n    \n  \n\n\n    \n\n        \n            \n                1\n                \n                2\n                \n                3\n            \n            Step 3 of 3\n        \n\n        \n            Complete Your Profile\n            \n                Just a few more details to get you started.\n            \n\n            \n\n                \n                    \n                        Country\n                        \n                            Select a Country\n                            United States\n                            Canada\n                            Mexico\n                            United Kingdom\n                            Australia\n                            Brazil\n                            China\n                            France\n                            Germany\n                            India\n                            Ireland\n                            Italy\n                            Japan\n                            Netherlands\n                            New Zealand\n                            Nigeria\n                            South Korea\n                            Spain\n                            Sweden\n                        \n                    \n\n                    \n                        State\n                        \n                            Select a State or Territory\n                            Alabama\n                            Alaska\n                            Arizona\n                            Arkansas\n                            California\n                            Colorado\n                            Connecticut\n                            Delaware\n                            District of Columbia\n                            Florida\n                            Georgia\n                            Hawaii\n                            Idaho\n                            Illinois\n                            Indiana\n                            Iowa\n                            Kansas\n                            Kentucky\n                            Louisiana\n                            Maine\n                            Maryland\n                            Massachusetts\n                            Michigan\n                            Minnesota\n                            Mississippi\n                            Missouri\n                            Montana\n                            Nebraska\n                            Nevada\n                            New Hampshire\n                            New Jersey\n                            New Mexico\n                            New York\n                            North Carolina\n                            North Dakota\n                            Ohio\n                            Oklahoma\n                            Oregon\n                            Pennsylvania\n                            Rhode Island\n                            South Carolina\n                            South Dakota\n                            Tennessee\n                            Texas\n                            Utah\n                            Vermont\n                            Virginia\n                            Washington\n                            West Virginia\n                            Wisconsin\n                            Wyoming\n                        \n                    \n                \n\n                \n                    \n                        City\n                        \n                    \n\n                    \n                        Zip Code\n                        \n                    \n                \n\n                \n                    Are you authorized to work in the U.S.?\n                    \n                        \n                            \n                            Yes\n                        \n\n                        \n                            \n                            No\n                        \n                    \n                \n\n                \n                    \n                        Disability Status\n                        \n                            Select Disability Status\n                            Yes\n                            No\n                            I Prefer Not to Say\n                        \n                    \n\n                    \n                        Veteran Status\n                        \n                            Select Veteran Status\n                            Yes\n                            No\n                            Protected Veteran\n                            Recently Separated Veteran\n                            Disabled Veteran\n                            I Prefer Not to Say\n                        \n                    \n                \n\n                \n                    Gender\n                    \n                        \n                            \n                            Male\n                        \n\n                        \n                            \n                            Female\n                        \n                    \n                \n\n                \n                    Ethnicity\n                    \n                        Select Ethnicity\n                        American Indian or Alaska Native\n                        Asian\n                        Black or African American\n                        Hispanic or Latino\n                        Native Hawaiian or Other Pacific Islander\n                        White\n                        Two or More Races\n                        Other\n                        I Prefer Not to Say\n                    \n                \n\n                \n                    Finalize & Submit\n                \n\n            \n        \n    \n\n\n\n    \n        \n            ✓\n            ApplyR\n        \n        © 2026 ApplyR. All rights reserved.\n    
"""



"""with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state("load")
    full_page_width = 1280
    page.set_viewport_size({"width": full_page_width, "height": full_page_height})
    body_text = page.locator("body").inner_text()
    image = pyautogui.screenshot(region=(100, 30, 1200, 780))
    image.show()"""
