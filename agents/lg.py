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
import math
import json
import time
import base64
from datetime import datetime
from agents.state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess, AITokens, QuestionProcess, AnswerItem, MarkdownProcess, ReviewMarkdownProcess, CompleteMarkdownProcess, ReviewClickAndViewProcess, FindIcon, ReviewQuestionProcess, SearchProcess, ReviewSearchProcess, CompleteSearchProcess, FindTimeProcess, TextTimeProcess, ReviewTimeProcess, CalendarTimeProcess, ReviewFindTimeProcess, ExtraStepsProcess, SetupSelectProcess, QuickSelectProcess, ReviewQuickProcess, QuickTimeProcess, DropdownProcess, QuickSearchProcess
import io
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import numpy as np
import requests
import cv2
import math
import subprocess
import supervision as sv
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
decide_page_llm = llm2.with_structured_output(DecidePage, include_raw=True)
apply_process_llm = llm2.with_structured_output(ApplyProcess, include_raw=True)
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
find_time_process_llm2 = llm2.with_structured_output(FindTimeProcess, include_raw=True)
review_find_time_process_llm2 = llm2.with_structured_output(ReviewFindTimeProcess, include_raw=True)
text_time_process_llm2 = llm2.with_structured_output(TextTimeProcess, include_raw=True)
review_time_process_llm2 = llm2.with_structured_output(ReviewTimeProcess, include_raw=True)
calendar_time_process_llm2 = llm2.with_structured_output(CalendarTimeProcess, include_raw=True)
extra_steps_process_llm2 = llm2.with_structured_output(ExtraStepsProcess, include_raw=True)
setup_select_process_llm2 = llm2.with_structured_output(SetupSelectProcess, include_raw=True)
quick_select_process_llm2 = llm2.with_structured_output(QuickSelectProcess, include_raw=True)
quick_time_process_llm2 = llm2.with_structured_output(QuickTimeProcess, include_raw=True)
review_quick_process_llm2 = llm2.with_structured_output(ReviewQuickProcess, include_raw=True)
dropdown_process_llm2 = llm2.with_structured_output(DropdownProcess, include_raw=True)
quick_search_process_llm2 = llm2.with_structured_output(QuickSearchProcess, include_raw=True)


url = "https://www.allstate.jobs/job/23890328/software-engineering-manager-java-/"
url = "https://www.allstate.jobs/job/23927829/software-engineer-all-levels-/"
url = "https://testing-kohl-psi.vercel.app/"
# url = "https://apply.deloitte.com/en_US/careers/InviteToApply?jobId=350244&source=LinkedIn"
# url = "https://job-boards.greenhouse.io/embed/job_app?token=8003605&for=coinbase&gh_src=wvu4737r1us&gh_jid=8003605"
url = "https://www.steelfab-inc.com/careers/software-developer-intern-charlotte-nc/?careers=Software%20Developer%20Intern%20Charlotte%20Nc&utm_source=ziprecruiter"
url = "https://jobs.intuit.com/job/-/-/27595/100620927520?cid=job_id_click_us_swe-fs-fy27_cn_text_job_int-tm&p_sid=DDYlORb&p_uid=ejALfQGNMq&ss=paid&utm_campaign=&utm_content=pj_board&utm_medium=jobad&utm_source=indeed+organic"
url = "https://talent.lowes.com/us/en/job/JR-02623542/Exploratory-Software-Engineering-Undergrad-Internship-Summer-2027?utm_source=617ZipRecruiterOrganic&cid=01a1f161-40bd-7568-9763-73aaeae1b8fd"
# url = "https://www.vanguardjobs.com/job/23948133/college-to-corporate-it-internship-application-development-nc-charlotte-nc/?utm_medium=%22mcloud-jobads%22&utm_campaign=Technology&utm_content=College%20to%20Corporate%20IT%20Internship-Application%20Development%20(NC)&utm_term=182781&source=Corporate_Website"
url = "https://jobs.newellbrands.com/job/Huntersville-2027-Newell-Brands-Intern-Sales-AI-&-Analytics-Developer-Intern-Nort/1431281200/?utm_source=ZipRecruiter&utm_campaign=J2W_ZIP"
url = "https://testing-kohl-psi.vercel.app/"
# url = "https://paypal.eightfold.ai/careers/job/274922982814?source=JobBoardIndeed-Organic"

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
    return new_tokens, model_name  


def empty_pixel_process(encoded_bytes: str, boxes_details: list[dict], full_page_width: int, full_page_height: int):
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-9"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image_width, image_height = image.size
    coordinates = []
    remove_columns = []
    remove_rows = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        bbox = current_box["bbox"]
        coordinate = [bbox[0], bbox[1], bbox[2], bbox[3]]
        coordinates.append(coordinate)

    for i in range(len(image_width)):
        remove_rows.append(i)
    
    for i in range(len(image_height)):
        remove_columns.append(i)

    
                           

def empty_pixel_process(encoded_bytes: str, boxes_details: list[dict], full_page_width: int, full_page_height: int):
    coordinates = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        bbox = current_box["bbox"]
        coordinates.append([bbox[0], bbox[1], bbox[2], bbox[3]])
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

def cropped_coordinates_process(full_page_height1: int, full_page_height2: int, min_cut_off_height: int, desired_bbox: list[float]):
    x1, y1, x2, y2 = desired_bbox

    y1_pixel = (y1 * full_page_height2) + min_cut_off_height
    y2_pixel = (y2 * full_page_height2) + min_cut_off_height

    new_bbox = [x1, y1_pixel / full_page_height1, x2, y2_pixel / full_page_height1]

    print(f"Original cropped bbox: {desired_bbox}")
    print(f"Converted bbox: {new_bbox}")
    print(f"Old height: {full_page_height1}")
    print(f"New height: {full_page_height2}")
    print(f"Top crop offset: {min_cut_off_height}")

    return new_bbox

def page_width_and_height_process(state: ApplicationState):
    page = state["current_page"]["page"]
    for i in range(500, 1401, 100):
        page.set_viewport_size({"width": i, "height": 500})
        real_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if real_height <= 4000:
            page.set_viewport_size({"width": i, "height": real_height})
            print(f"image width: {i}")
            print(f"image height: {real_height}")
            return i, real_height
    real_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight )}""")
    print(f"image width: {i}")
    print(f"image height: {real_height}")
    page.set_viewport_size({"width": 1300, "height": real_height})
    return 1400, real_height

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
"""
def omniparser_process(state: ApplicationState, encoded_bytes=None, full_page_width=None, full_page_height=None):
    page = state["current_page"]["page"]
    if not encoded_bytes:"""
        # full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
"""encoded_bytes, full_page_width, full_page_height = screenshot_process(state)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image_width, image_height = image.size
    print(f"image pixel height: {image_height}")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    response_data = response.json()
    encoded_bytes = response_data["encoded_bytes"]
    boxes_details = response_data["boxes_details"]"""
    # full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    # return encoded_bytes, boxes_details, full_page_width, full_page_height


class BoxAnnotator:
    def __init__(self, text_scale=0.8, text_padding=5, text_thickness=2, thickness=1, avoid_overlap=True):
        self.text_scale = text_scale
        self.text_padding = text_padding
        self.text_thickness = text_thickness
        self.thickness = thickness
        self.avoid_overlap = avoid_overlap

    def annotate(self, scene: np.ndarray, detections, labels=None, image_size=None):
        annotated_frame = scene.copy()
        height, width = annotated_frame.shape[:2]

        if image_size is not None:
            width, height = image_size

        boxes = detections.xyxy.astype(int)

        if labels is None:
            labels = [str(i) for i in range(len(boxes))]

        color = (65, 65, 255)  # Red in OpenCV BGR format
        font = cv2.FONT_HERSHEY_SIMPLEX

        for i, (x1, y1, x2, y2) in enumerate(boxes):
            x1 = max(0, min(int(x1), width - 1))
            y1 = max(0, min(int(y1), height - 1))
            x2 = max(0, min(int(x2), width - 1))
            y2 = max(0, min(int(y2), height - 1))

            if x2 <= x1 or y2 <= y1:
                continue

            # Draw thin red bounding box.
            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                color,
                self.thickness
            )

            label = str(labels[i])

            # Use small labels like the original OmniParser.
            font_scale = 0.3
            font_thickness = 1

            (text_width, text_height), baseline = cv2.getTextSize(
                label,
                font,
                font_scale,
                font_thickness
            )

            padding = 2
            label_width = text_width + padding * 2
            label_height = text_height + padding * 2

            # Default: top-left, just above the box.
            label_x = x1
            label_y = y1 - label_height

            # If too close to the top, put label inside.
            if label_y < 0:
                label_y = y1

            # Keep label inside the image horizontally.
            if label_x + label_width > width:
                label_x = max(0, width - label_width)

            # Try alternative positions if the label
            # overlaps another detection.
            if self.avoid_overlap:
                positions = [
                    (label_x, label_y),
                    (x1, y1),
                    (x2, y1),
                    (x1, y2)
                ]

                for candidate_x, candidate_y in positions:
                    candidate_x = int(candidate_x)
                    candidate_y = int(candidate_y)

                    lx1 = candidate_x
                    ly1 = candidate_y
                    lx2 = lx1 + label_width
                    ly2 = ly1 + label_height

                    if lx1 < 0 or ly1 < 0 or lx2 > width or ly2 > height:
                        continue

                    overlaps = False

                    for j, (bx1, by1, bx2, by2) in enumerate(boxes):
                        if j == i:
                            continue

                        intersection_width = max(
                            0,
                            min(lx2, bx2) - max(lx1, bx1)
                        )

                        intersection_height = max(
                            0,
                            min(ly2, by2) - max(ly1, by1)
                        )

                        intersection_area = intersection_width * intersection_height
                        label_area = label_width * label_height

                        if label_area > 0 and intersection_area / label_area > 0.3:
                            overlaps = True
                            break

                    if not overlaps:
                        label_x = candidate_x
                        label_y = candidate_y
                        break

            # Draw red label background.
            cv2.rectangle(
                annotated_frame,
                (label_x, label_y),
                (label_x + label_width, label_y + label_height),
                color,
                cv2.FILLED
            )

            # Draw white number.
            cv2.putText(
                annotated_frame,
                label,
                (label_x + padding, label_y + padding + text_height),
                font,
                font_scale,
                (255, 255, 255),
                font_thickness,
                cv2.LINE_AA
            )

        return annotated_frame




def omniparser_process(state: ApplicationState, encoded_bytes=None, full_page_width=None, full_page_height=None):
    page = state["current_page"]["page"]

    if not encoded_bytes:
        encoded_bytes, full_page_width, full_page_height = screenshot_process(state)

    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    image = Image.open(io.BytesIO(decoded_bytes)).convert("RGB")

    image_width, image_height = image.size

    max_height = 3000
    all_boxes_details = []

    # STEP 1: Split the image into chunks and run OmniParser.
    for start_y in range(0, image_height, max_height):
        end_y = min(start_y + max_height, image_height)

        cropped_image = image.crop((0, start_y, image_width, end_y))
        cropped_width, cropped_height = cropped_image.size

        buffer = io.BytesIO()
        cropped_image.save(buffer, format="PNG")

        cropped_encoded_bytes = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        data = {
            "image_input": cropped_encoded_bytes,
            "box_threshold": 0.05,
            "iou_threshold": 0.10,
            "use_paddleocr": True,
            "imgsz": 640
        }

        response = requests.post(
            "http://127.0.0.1:8000/image_process",
            json=data,
            timeout=180
        )

        response.raise_for_status()

        response_data = response.json()
        chunk_boxes_details = response_data["boxes_details"]

        # STEP 2: Convert chunk coordinates to full-image coordinates.
        for box in chunk_boxes_details:
            box = box.copy()

            x1, y1, x2, y2 = box["bbox"]

            box["bbox"] = [
                (x1 * cropped_width) / image_width,
                (y1 * cropped_height + start_y) / image_height,
                (x2 * cropped_width) / image_width,
                (y2 * cropped_height + start_y) / image_height
            ]

            # Remove any old ID field.
            box.pop("id", None)

            all_boxes_details.append(box)

    # STEP 3: Sort all elements globally by Y, then X.
    all_boxes_details.sort(
        key=lambda box: (
            box["bbox"][1],
            box["bbox"][0]
        )
    )

    # STEP 4: Renumber the actual icon field sequentially.
    for index, box in enumerate(all_boxes_details):
        box["icon"] = index

    # STEP 5: Verify that icons are sequential and unique.
    icons = [box["icon"] for box in all_boxes_details]

    assert icons == list(range(len(all_boxes_details))), (
        "OmniParser icon numbering is not sequential."
    )

    # STEP 6: Prepare bounding boxes and labels.
    # The labels use the NEW icon values.
    xyxy = []
    labels = []

    for box in all_boxes_details:
        x1, y1, x2, y2 = box["bbox"]

        xyxy.append([
            x1 * image_width,
            y1 * image_height,
            x2 * image_width,
            y2 * image_height
        ])

        labels.append(str(box["icon"]))

    # STEP 7: Draw bounding boxes after sorting and renumbering.
    annotated_frame = np.asarray(image).copy()

    if xyxy:
        detections = sv.Detections(
            xyxy=np.asarray(xyxy, dtype=np.float32)
        )

        box_annotator = BoxAnnotator(
            text_scale=0.2,
            text_padding=2,
            text_thickness=2,
            thickness=1,
            avoid_overlap=True
        )

        annotated_frame = box_annotator.annotate(
            scene=annotated_frame,
            detections=detections,
            labels=labels,
            image_size=(image_width, image_height)
        )

    # STEP 8: Encode the annotated screenshot.
    annotated_image = Image.fromarray(annotated_frame)

    output_buffer = io.BytesIO()
    annotated_image.save(output_buffer, format="PNG")

    annotated_encoded_bytes = base64.b64encode(
        output_buffer.getvalue()
    ).decode("utf-8")

    # STEP 9: Return full-image dimensions.
    full_page_width = image_width
    full_page_height = image_height

    return annotated_encoded_bytes, all_boxes_details, full_page_width, full_page_height


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
    page = state["current_page"]["page"]
    context = state["context"]
    print(f"context: {context}")
    print(f"context pages: {context.pages}")
    # encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    # encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    # image.show()
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        box_type = current_box["type"]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])

    body_text = page.locator("body").inner_text() or ""
    token_usage = state.get("token_usage")
    prompt = f"""Your an AI Application Helper and your job is to decide what page this is.
    Look at the Image, the page elements, and the body text to determine what page this is.

    Body Text: {body_text}

    Page Elements Format:
    [icon, type, coordinates, content]

    Page Elements: {page_elements}

    You have to determine what type of page we are looking at.

    1. cookies - You always choose this page if there are cookies on the page.
    2. apply - You choose this page if we need to click apply now, apply manually to start the application.
    3. forms - You choose this page if there is forms that need to be filled.
    4. verification - You choose this page if there is a verification code that needs to be filled out, or if you need to verify an email, anything to do with verifying an account.
    5. exit - You choose this page if there the url isn't active.
    6. wait - if the page is blank and has nothing forms, steps, or content on the page then choose the wait process. 
    7. complete - If the application is the complete and fully submitted please mark this as complete so we can tell the user that his application is fully submitted.

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
    elif action == "wait":
        wait_tracker = state["wait_tracker"]
        wait_tracker += 1
        state["wait_tracker"] = wait_tracker
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
        state["wait_tracker"] = 0
        return "apply"
    elif action == "cookies":
        state["wait_tracker"] = 0
        return "cookies"
    elif action == "signup":
        state["wait_tracker"] = 0
        return "signup"
    elif action == "forms":
        state["wait_tracker"] = 0
        return "forms"
    elif action == "application":
        state["wait_tracker"] = 0
        return "application"
    elif action == "verification":
        state["wait_tracker"] = 0
        return "verification"
    elif action == "wait":
        wait_tracker = state["wait_tracker"]
        print(f"wait tracker: {wait_tracker}")
        if wait_tracker >= 3:
            state["leaving_reason"] = "Wait tracker hit 3."
            return "exit"
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
    page = state["current_page"]["page"]
    print(f"page: {page}")
    print("we are in the wait process")
    time.sleep(3)
    body_text = page.locator("body").inner_text()
    if len(body_text) > 20:
        state["wait_action"] = "continue"
        return state
    time.sleep(30)
    if len(body_text) > 20:
        state["wait_action"] = "continue"
    else:
        state["wait_action"] = "exit"
        state["leaving_reason"] = "The page would not load"
    return state

def wait_routing(state: ApplicationState):
    wait_action = state.get("wait_action")
    if wait_action == "continue":
        return "continue"
    else:
        return "exit"
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
    body_text = page.locator("body") or ""
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        box_type = current_box["type"]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, content])
    prompt = f"""
You are an AI Applicant Helper.

Your goal is to start or continue the job application process.

You will receive:
1. A screenshot of the webpage.
2. The body text
3. The detected interface elements in Page Elements.

Use the screenshot, body text, and Page Elements to determine which icon should be clicked.

Page Elements Format:
[icon, type, coordinates, content]

PAGE ELEMENTS
{page_elements}

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
    all_reasons = []

    previous_answers = []

    for attempt in range(5):
        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
        encoded_bytes2, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        decoded_bytes2 = base64.b64decode(encoded_bytes2.encode("utf-8"))
        buffer = io.BytesIO(decoded_bytes2)
        image = Image.open(buffer)
        # image.show()
        page_elements = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            bbox = current_box["bbox"]
            coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
            box_type = current_box["type"]
            content = current_box["content"]
            page_elements.append([icon, coordinates, content])
    
        white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details, full_page_width=full_page_width, full_page_height=full_page_height)
        body_text = page.locator("body").inner_text() or ""
        # print(f"page elements: {page_elements}")
        prompt = f"""
You are completing a job application form using the user's profile and the visible page.
You need to look at the images to think logically on how to answer the questions and deal with errors.
Just think of your self as a master in filling out applications and do the things that would make you the best auto applier for the user.

GOAL
- Correctly answer every required question.
- Fix visible validation errors.
- If a question is answered leave unchanged unl
- Use the user's profile first and reasonable inference when necessary.
- Return an action for every relevant visible question.
- Use the input/option icon, not the question-label icon, when possible.

ACTIONS
skip: No change needed or question should be skipped.
fill: Fill an empty input. Requires action_text + icon. (don't use fill for time questions)
delete: Clear incorrect/unwanted text. Requires icon.
delete_and_fill: Delete text and fill it in with new text.
click: Select/unselect an immediately answerable option. Requires icon.
upload_resume: Resume upload field. Requires icon.
upload_cover_letter: Cover-letter upload field. Requires icon.
extra_steps: we use this for time questions, dropdown questions, or when we need to search to answer the question. Requires icon + Current Question with guidance between (search, dropdown, time).
click_and_view: Click only when it reveals additional fields/questions that must be completed. Requires icon + question.
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
[icon, coordinates, content]

PAGE ELEMENTS
{page_elements}

Body Text:
{body_text}

ITEMS ELEMENTS

skip: [action, reason]

fill: [action, icon, action_text, reason]

delete: [action, icon, reason]

delete_and_fill: [action, icon, action_text, reason]

click: [action, icon, reason]

upload_resume: [action, icon, reason]

upload_cover_letter: [action, icon, reason]

extra_steps: [action, icon, current_question, reason]

click_and_view: [action, icon, current_question, reason]

submit: [action, icon, submit_text, reason]

ACTIONS

Example:

items: [["skip"], ["fill", 28, {state["email"]}], ["delete", 5] ["delete_and_fill", 75, "{state["country"]}], ["click", 32], ["upload_resume", 50], ["upload_cover_letter", 52], ["extra_steps", 20, "What skills do you have"] ["click_and_view", 22, "Add More Work Experience"], ["submit", 30]]
error: yes there was an error on checking a box and I handled it by clicking a box to fix it.

Current Attempt on Page: {attempt}

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
        state, decision, all_reasons = review_answer_question_process(state=state, all_text=all_text, all_reasons=all_reasons)
        del all_text[-1]
        if decision == "same_form":
            continue
        elif decision == "new_form":
            state["signup_action"] = "new_form"
            return state
        elif decision == "different_page":
            state["signup_action"] = "different_page"
            return state
        elif decision == "complete":
            state["signup_action"] = "complete"
            return state

    state["signup_action"] = "max_tries"
    state["leaving_reason"] = "Max tries for the forms process"
    return state

def review_answer_question_process(state: ApplicationState, all_text: list[str], all_reasons: list[str]):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image.show()
    total_cost = state["token_usage"]["total_cost"]
    if total_cost >= 0.10:
        state["leaving_reason"] = "Total cost greater than $0.10"
        return state, "total_cost"
    full_text = page.locator("body").inner_text()

    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        page_elements.append([icon, coordinates, content])

    body_text = " ".join(full_text.split()[:100])
    all_text.append(body_text)
    print(f"all reasons: {all_reasons}")
    prompt = f"""
Your an AI Applicant helper and your job is to look at the two different lists of body text and determine.
1. same_form - The questions on the page are mostly the same.
2. new_form - The questions on the page are new.
3. different_page - This new page text is not questions and are something different.
4. complete - If you see a message or look within the photo and see that the application is complete and fully submitted mark this as complete.

Look at the image to determine if the application is fully complete and submitted.

Old Page Text: {all_text[0]}

New Page Text: {all_text[1]}

All reasons for choosing a type of form/page so far: {all_reasons}
Ex 1:
{{decision: same_form, reason: your reason}}

Page Elements Format:
[icon, coordinates, content]

Page Elements: {page_elements}

Sometimes all we need to do is click one icon to help complete the form

{{decision: same_form, action: click, icon: 12, reason: your reason}}

Ex 2:
{{decision: new_form, reason: your reason}}

Ex 3:
{{decision: different_page, reason: your reason}}

Ex 4:
{{decision: complete, reason: your reason}}
"""
    response = review_question_process_llm3.invoke([
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
        state["leaving_reason"] = f"The cost extended above $0.10 at the review signup page process with the total being ${total_cost}"

    answers = response["parsed"]
    print(f"Review Answers: {answers}")
    decision = answers.get("decision")
    reason = answers.get("reason")
    action = answers.get("action")
    icon = answers.get("icon")
    if action == "click" and icon is not None:
        current_box = boxes_details[icon]
        current_answer = [action, icon]
        context = state.get("context")
        page_count = len(context.pages)
        state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)

    all_reasons.append(reason)
    return state, decision, all_reasons

def action_process(ai_answers: list[list], boxes_details: list[dict], state: ApplicationState, full_page_width: int, full_page_height: int, white_x=None, white_y=None, process=None, page_count=None):
    ai_answers.sort(key=lambda x: {"skip": 0, "fill": 1, "delete": 2, "click": 3, "extra_steps": 4, "upload_resume": 5, "upload_cover_letter": 6, "click_and_view": 7, "add_more": 8, "submit": 9}.get(x[0].lower(), 999))
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
    print(f"current answer: {current_answer}")
    if not action or action == "skip":
        return state
    if action != "arrow":
        icon = current_answer[1] if len(current_answer ) > 1 else None
        if icon is None or not isinstance(icon, int):
            return state
        if icon >= 0:
            coordinates = current_box.get("bbox")
            page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
            print(f"page_x: {page_x}, page_y: {page_y}")
    context = state.get("context")

    if action == "fill":
        action_text = current_answer[2] if len(current_answer ) > 2 else None
        if not action_text:
            action_text = ""
        for i in range(1000):
            page.keyboard.press("ArrowRight")
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
        if full_page_height >= 500:
            full_page_height = 500
        pyautogui_image = pyautogui.screenshot(region=(40, 120, full_page_width, full_page_height))
        buffer = io.BytesIO()
        pyautogui_image.save(buffer, format="PNG")
        pyautogui_bytes = buffer.getvalue()
        encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
        encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(encoded_bytes=encoded_bytes, full_page_width=full_page_width, full_page_height=full_page_height, state=state)
        white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details, full_page_width=full_page_width, full_page_height=full_page_height)
        white_x += 40
        white_y += 120
        print(f"white x: {white_x}, white y: {white_y}")
        pyautogui.click(x=white_x, y=white_y)
        time.sleep(0.1)
        pyautogui.moveTo(0, 0)
    elif action == "extra_steps":
        current_question = current_answer[2] if len(current_answer ) > 2 else None
        current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
        if current_height != full_page_height:
            print("used find icon for time")
            encoded_bytes, page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        page.mouse.click(page_x, page_y)
        new_page_count = len(context.pages)
        if new_page_count > page_count:
            all_pages = context.pages
            all_pages[-1].close()
        pyautogui.hotkey("down")
        state = extra_steps_process(current_answer=current_answer, old_encoded_bytes=encoded_bytes, old_boxes_details=boxes_details, old_page_width=full_page_width, old_page_height=full_page_height, page_x=page_x, page_y=page_y, cut_off_height=page_y, state=state)
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
        desired_option = current_answer[2]
        option_difference = desired_option - current_option
        if option_difference == 0:
            pyautogui.hotkey("enter")

        elif option_difference > 0:
            for i in range(option_difference):
                pyautogui.hotkey("down")
                print(f"pressed down {i+1} times")
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

def pixel_image_cropping(encoded_bytes1: str, encoded_bytes2: str, full_page_width=None, top_height1=None, bottom_height1=None, top_height2=None, bottom_height2=None):

    decoded_bytes = base64.b64decode(encoded_bytes1.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image1 = Image.open(buffer)
    image1_width, image1_height = image1.size
    image1_matrix = np.array(image1)

    decoded_bytes = base64.b64decode(encoded_bytes2.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image2 = Image.open(buffer)
    image2_width, image2_height = image2.size
    image2_matrix = np.array(image2)

    if full_page_width is None:
        full_page_width = image2_width

    # FULL IMAGE PIXEL COMPARISON

    if top_height1 is None:

        cut_off_top_height = None
        cut_off_bottom_height = None

        comparison_height = min(image1_height, image2_height)

        for i in range(comparison_height):
            image1_row = image1_matrix[i]
            image2_row = image2_matrix[i]

            if not np.array_equal(image1_row, image2_row):
                cut_off_top_height = i
                break

        for i in range(comparison_height - 1, -1, -1):
            image1_row = image1_matrix[i]
            image2_row = image2_matrix[i]

            if not np.array_equal(image1_row, image2_row):
                cut_off_bottom_height = i + 1
                break

        if cut_off_top_height is None or cut_off_bottom_height is None:
            return encoded_bytes2, None, None

    # BOUNDING BOX ANCHOR PIXEL COMPARISON

    else:

        cut_off_top_height = top_height2
        cut_off_bottom_height = bottom_height2

        if any(
            value is None
            for value in (
                top_height1,
                top_height2,
                bottom_height1,
                bottom_height2
            )
        ):
            return encoded_bytes2, None, None

        top_steps = min(
            image1_height - top_height1,
            image2_height - top_height2
        )

        for offset in range(top_steps):
            image1_row = image1_matrix[top_height1 + offset]
            image2_row = image2_matrix[top_height2 + offset]

            if not np.array_equal(image1_row, image2_row):
                cut_off_top_height = top_height2 + offset
                break

        bottom_steps = min(
            bottom_height1 + 1,
            bottom_height2 + 1
        )

        for offset in range(bottom_steps):
            image1_row = image1_matrix[bottom_height1 - offset]
            image2_row = image2_matrix[bottom_height2 - offset]

            if not np.array_equal(image1_row, image2_row):
                cut_off_bottom_height = bottom_height2 - offset + 1
                break

    cut_off_top_height = max(0, min(image2_height, cut_off_top_height))
    cut_off_bottom_height = max(0, min(image2_height, cut_off_bottom_height))

    if cut_off_top_height >= cut_off_bottom_height:
        return encoded_bytes2, None, None

    cropped_image = image2.crop((0, cut_off_top_height, min(full_page_width, image2_width), cut_off_bottom_height))

    buffer = io.BytesIO()
    cropped_image.save(buffer, format="PNG")

    decoded_bytes = buffer.getvalue()
    encoded_bytes = base64.b64encode(decoded_bytes).decode("utf-8")

    return encoded_bytes, cut_off_top_height, cut_off_bottom_height


def cropped_image_process(encoded_bytes1: str, encoded_bytes2: str, boxes_details1: list[dict], boxes_details2: list[dict], cut_off_height: int, full_page_width: int, old_page_height: int, state: ApplicationState):
    decoded_bytes = base64.b64decode(encoded_bytes1.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image1 = Image.open(buffer)
    image1_width, image1_height = image1.size
    image1_matrix = np.array(image1)

    decoded_bytes = base64.b64decode(encoded_bytes2.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image2 = Image.open(buffer)
    image2_width, image2_height = image2.size
    image2_matrix = np.array(image2)

    page = state["current_page"]["page"]

    current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    if current_height != old_page_height:

        above_list1 = []
        below_list1 = []
        above_list2 = []
        below_list2 = []

        for i in range(len(boxes_details1)):
            current_box = boxes_details1[i]
            content = current_box["content"]
            bbox = current_box["bbox"]

            current_box_height = old_page_height * (
                (bbox[1] + bbox[3]) / 2
            )

            if current_box_height > cut_off_height:
                below_list1.append([current_box_height, content, current_box])
            else:
                above_list1.append([current_box_height, content, current_box])

        for l in range(len(boxes_details2)):
            current_box = boxes_details2[l]
            content = current_box["content"]
            bbox = current_box["bbox"]

            current_box_height = current_height * ((bbox[1] + bbox[3]) / 2)

            if current_box_height > cut_off_height:
                below_list2.append([current_box_height, content, current_box])
            else:
                above_list2.append([current_box_height, content, current_box])

        below_list1.sort(key=lambda x: x[0])
        below_list2.sort(key=lambda x: x[0])
        above_list1.sort(key=lambda x: x[0], reverse=True)
        above_list2.sort(key=lambda x: x[0], reverse=True)

        top_height1 = None
        top_height2 = None
        bottom_height1 = None
        bottom_height2 = None

        top_finished = False
        bottom_finished = False

        # TOP BOUNDING BOX MATCHING

        for i in range(len(above_list1)):
            if top_finished:
                break

            first_content = above_list1[i][1]

            for l in range(len(above_list2)):
                if top_finished:
                    break

                second_content = above_list2[l][1]

                if first_content == second_content:
                    first_box = above_list1[i][2]
                    second_box = above_list2[l][2]

                    temp_top_height1 = round(image1_height * ((first_box["bbox"][1] + first_box["bbox"][3]) / 2))

                    temp_top_height2 = round(image2_height * ((second_box["bbox"][1] + second_box["bbox"][3]) / 2))

                    temp_top_height1 = max(0, min(image1_height - 1, temp_top_height1))
                    temp_top_height2 = max(0, min(image2_height - 1, temp_top_height2))

                    first_row = image1_matrix[temp_top_height1]
                    second_row = image2_matrix[temp_top_height2]

                    if np.array_equal(first_row, second_row):
                        top_height1 = temp_top_height1
                        top_height2 = temp_top_height2
                        top_finished = True
                        break

                    start = max(0, temp_top_height2 - 5)
                    end = min(image2_height, temp_top_height2 + 6)

                    for j in range(start, end):
                        second_row = image2_matrix[j]

                        if np.array_equal(first_row, second_row):
                            top_height1 = temp_top_height1
                            top_height2 = j
                            top_finished = True
                            break

        # BOTTOM BOUNDING BOX MATCHING

        for i in range(len(below_list1)):
            if bottom_finished:
                break

            first_content = below_list1[i][1]

            for l in range(len(below_list2)):
                if bottom_finished:
                    break

                second_content = below_list2[l][1]

                if first_content == second_content:
                    first_box = below_list1[i][2]
                    second_box = below_list2[l][2]

                    temp_bottom_height1 = round(image1_height * ((first_box["bbox"][1] + first_box["bbox"][3]) / 2))

                    temp_bottom_height2 = round(image2_height * ((second_box["bbox"][1] + second_box["bbox"][3]) / 2))

                    temp_bottom_height1 = max(0, min(image1_height - 1, temp_bottom_height1))

                    temp_bottom_height2 = max(0, min(image2_height - 1, temp_bottom_height2))

                    first_row = image1_matrix[temp_bottom_height1]
                    second_row = image2_matrix[temp_bottom_height2]

                    if np.array_equal(first_row, second_row):
                        bottom_height1 = temp_bottom_height1
                        bottom_height2 = temp_bottom_height2
                        bottom_finished = True
                        break

                    start = max(0, temp_bottom_height2 - 5)
                    end = min(image2_height, temp_bottom_height2 + 6)

                    for j in range(start, end):
                        second_row = image2_matrix[j]

                        if np.array_equal(first_row, second_row):
                            bottom_height1 = temp_bottom_height1
                            bottom_height2 = j
                            bottom_finished = True
                            break

        # CALL PIXEL IMAGE CROPPING WITH MATCHED ANCHORS

        if (top_finished and bottom_finished and top_height1 < bottom_height1 and top_height2 < bottom_height2):
            return pixel_image_cropping(
                encoded_bytes1=encoded_bytes1,
                encoded_bytes2=encoded_bytes2,
                full_page_width=full_page_width,
                top_height1=top_height1,
                bottom_height1=bottom_height1,
                top_height2=top_height2,
                bottom_height2=bottom_height2
            )

        # FALLBACK WHEN BOUNDING BOX MATCHING FAILS

        return pixel_image_cropping(
            encoded_bytes1=encoded_bytes1,
            encoded_bytes2=encoded_bytes2,
            full_page_width=full_page_width
        )

    else:
        print("going through pixel process normally")

        return pixel_image_cropping(
            encoded_bytes1=encoded_bytes1,
            encoded_bytes2=encoded_bytes2,
            full_page_width=full_page_width
        )

def compare_pixel(encoded_bytes1: str, encoded_bytes2: str):
    decoded_bytes1 = base64.b64decode(encoded_bytes1.encode("utf-8"))
    buffer1 = io.BytesIO(decoded_bytes1)
    image1 = Image.open(buffer1).convert("RGB")
    image1_width, image1_height = image1.size

    decoded_bytes2 = base64.b64decode(encoded_bytes2.encode("utf-8"))
    buffer2 = io.BytesIO(decoded_bytes2)
    image2 = Image.open(buffer2).convert("RGB")
    image2_width, image2_height = image2.size

    if image1_width != image2_width or image1_height != image2_height:
        return False

    image1_array = np.array(image1)
    image2_array = np.array(image2)

    return bool(np.array_equal(image1_array, image2_array))


def expand_image(encoded_bytes: str):
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)

    width, height = image.size
    left_padding = 0
    top_padding = 0
    expanded_width = width
    expanded_height = height

    if width < 3500 or height < 100:
        background_color = image.getpixel((0, height // 2))

        padding = max(0, 3500 - width)
        left_padding = padding // 2
        expanded_width = max(3500, width)

        height_padding = max(0, 100 - height)
        top_padding = height_padding // 2
        expanded_height = max(100, height)

        expanded = Image.new(
            "RGB",
            (expanded_width, expanded_height),
            background_color
        )

        expanded.paste(image, (left_padding, top_padding))

        buffer = BytesIO()
        expanded.save(buffer, format="PNG")

        encoded_bytes = base64.b64encode(buffer.getvalue()).decode("utf-8")


    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}

    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    response_data = response.json()

    encoded_bytes = response_data["encoded_bytes"]
    boxes_details = response_data["boxes_details"]

    # Remove padding from the processed image
    if left_padding > 0 or top_padding > 0:
        processed_image = Image.open(
            BytesIO(base64.b64decode(encoded_bytes))
        )

        processed_image = processed_image.crop((
            left_padding,
            top_padding,
            left_padding + width,
            top_padding + height
        ))

        buffer = BytesIO()
        processed_image.save(buffer, format="PNG")

        encoded_bytes = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Restore normalized bounding box coordinates
        for box in boxes_details:
            if "bbox" in box:
                bbox = box["bbox"]

                bbox[0] = (bbox[0] * expanded_width - left_padding) / width
                bbox[2] = (bbox[2] * expanded_width - left_padding) / width
                bbox[1] = (bbox[1] * expanded_height - top_padding) / height
                bbox[3] = (bbox[3] * expanded_height - top_padding) / height

    return encoded_bytes, boxes_details




def check_search_options(old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, cropped_encoded_bytes: str, cropped_boxes_details1: list[dict], list_text: list[str], state: ApplicationState, used_enter: bool = False):
    page = state["current_page"]["page"]

    if not list_text:
        return False, state

    def combine_text(boxes_details, search_text):
        search_text = normalize_text(search_text)

        reorganized_elements = sorted(boxes_details, key=lambda current_box: (current_box["bbox"][0], current_box["bbox"][1]))

        combined_text = ""

        for current_box in reorganized_elements:
            content = normalize_text(current_box["content"])

            if not content:
                continue

            combined_text += content

        if search_text:
            combined_text = combined_text.replace(search_text, "", 1)

        return combined_text

    def replace_search_text(text):
        page.keyboard.press("ControlOrMeta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(text)

    original_text = combine_text(boxes_details=cropped_boxes_details1, search_text=list_text[0])

    for i in range(len(list_text)):
        print(f"Checking search option: {list_text[i]}")

        if page.is_closed():
            print("Page closed during check_search_options.")
            return False, state

        encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)

        if full_page_height == old_page_height:
            cropped_bytes, min_cut_off_height, max_cut_off_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=encoded_bytes)
        else:
            do_not_use_bytes, current_boxes_details, full_page_width, full_page_height = omniparser_process(state=state)

            cropped_bytes, min_cut_off_height, max_cut_off_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=encoded_bytes, boxes_details2=current_boxes_details, cut_off_height=cut_off_height, full_page_width=full_page_width, old_page_height=old_page_height, state=state)

        expanded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(encoded_bytes=cropped_bytes, state=state)

        current_text = combine_text(boxes_details=boxes_details, search_text=list_text[i])

        if not compare_text(text1=original_text, text2=current_text):
            print(f"Search options changed for: {list_text[i]}")
            return False, state

        if i < len(list_text) - 1:
            replace_search_text(list_text[i + 1])

    if used_enter:
        replace_search_text(list_text[0])
        page.keyboard.press("Enter")
    else:
        replace_search_text(list_text[0])

    print("Search options check completed.")

    return True, state


def quick_select_process(current_answer: dict, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator("select:focus")
    has_type = active_element.count() == 1

    if not has_type:
        active_element = page.evaluate_handle("document.activeElement").as_element()

        if active_element:
            tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
            has_type = tag_name == "select"

    if not has_type:
        return False, state

    total_options = active_element.locator("option").all_text_contents()

    if not total_options:
        return False, state

    prompt = f"""

You're an AI Applicant helper in the quick select process.

You're job is to look at the current question, the options available, and the USER PROFILE to answer the question to the best of your ability.
 
 Current Question: {current_answer}
 
 Every option: {total_options}

Example response 1: {{desired_option: 8}}

Example response 2: {{desired_option: None}}
 
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

    response = quick_select_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ])

    details = response["raw"]
    new_tokens, model_name = details_process(details=details)

    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)

    answer = response["parsed"]
    desired_option = answer.get("desired_option")

    if not isinstance(desired_option, int) or isinstance(desired_option, bool) or desired_option < 0 or desired_option >= len(total_options):
        return False, state

    if active_element.locator("option").nth(desired_option).is_disabled():
        return False, state

    desired_text = total_options[desired_option].strip()

    try:
        active_element.select_option(index=desired_option)
    except Exception:
        return False, state

    complete, state = review_quick_process(current_answer=current_answer, desired_text=desired_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    return complete, state


def adaptive_select_process(current_answer: dict, total_options: list[str], old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]

    prompt = f"""

You're an AI Applicant helper in the quick select process.

You're job is to look at the current question, the options available, and the USER PROFILE to answer the question to the best of your ability.
 
 Current Question: {current_answer}
 
 Every option: {total_options}

Example response 1: {{desired_option: 8}}

Example response 2: {{desired_option: None}}
 
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

    response = quick_select_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ])

    details = response["raw"]
    new_tokens, model_name = details_process(details=details)

    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)

    answer = response["parsed"]
    desired_option = answer.get("desired_option")
    return desired_option, state

def quick_rippling_select_process(current_answer: dict, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]

    # First method: Find the active element through Playwright.
    active_element = page.locator(":focus")
    has_type = False

    check_script = """
    (element) => {
        return element.matches('[role="combobox"]')
            || !!element.closest('[role="combobox"]');
    }
    """

    if active_element.count() == 1:
        has_type = active_element.evaluate(check_script)

    # Second method: Find the deeply focused element.
    if not has_type:
        focus_script = """
        () => {
            let active = document.activeElement;

            while (active?.shadowRoot?.activeElement) {
                active = active.shadowRoot.activeElement;
            }

            return active;
        }
        """

        active_element = page.evaluate_handle(focus_script).as_element()

        if active_element:
            has_type = active_element.evaluate(check_script)

    if not has_type:
        return False, state

    # Wait for the dropdown options to load.
    time.sleep(5)

    # Retrieve options from the dropdown associated with the active element.
    dropdown_script = """
    (element) => {
        const dropdown = element.matches('[role="combobox"]')
            ? element
            : element.closest('[role="combobox"]');

        if (!dropdown || dropdown.getAttribute("aria-expanded") !== "true") {
            return null;
        }

        const resultsId = dropdown.getAttribute("aria-controls");

        if (!resultsId) return null;

        const results = document.getElementById(resultsId);

        if (!results) return null;

        const options = [...results.querySelectorAll('li[role="option"]')]
            .filter(option => option.getAttribute("aria-disabled") !== "true")
            .map(option => ({
                index: option.getAttribute("data-idx"),
                text: option.textContent.trim(),
                id: option.id
            }));

        return {
            results_id: resultsId,
            options: options
        };
    }
    """

    dropdown_details = active_element.evaluate(dropdown_script)

    if not dropdown_details:
        return False, state

    results_id = dropdown_details["results_id"]
    options = dropdown_details["options"]

    if not options:
        return False, state

    total_options = [option["text"] for option in options]

    # Let the LLM choose the desired option.
    desired_option, state = adaptive_select_process(current_answer=current_answer, total_options=total_options, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    if desired_option is None:
        return False, state

    try:
        desired_option = int(desired_option)
    except (TypeError, ValueError):
        return False, state

    if not 0 <= desired_option < len(options):
        return False, state

    selected_option = options[desired_option]
    desired_text = selected_option["text"]
    option_id = selected_option["id"]

    # Click the selected option using JavaScript.
    clicked = page.evaluate("""
    ({resultsId, optionId, desiredText}) => {
        const results = document.getElementById(resultsId);
        const option = document.getElementById(optionId);

        if (!results || !option || !results.contains(option)) return false;
        if (option.textContent.trim() !== desiredText) return false;
        if (option.getAttribute("aria-disabled") === "true") return false;

        option.click();
        return true;
    }
    """, {"resultsId": results_id, "optionId": option_id, "desiredText": desired_text})

    if not clicked:
        return False, state

    # Review the selected answer.
    complete, state = review_quick_process(current_answer=current_answer, desired_text=desired_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    return complete, state

def quick_workday_select_process(current_answer: dict, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator(":focus")
    has_type = False

    if active_element.count() == 1:
        tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
        haspopup = active_element.get_attribute("aria-haspopup")
        has_type = tag_name == "button" and haspopup == "listbox"

    if not has_type:
        active_element = page.evaluate_handle("document.activeElement").as_element()

        if active_element:
            tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
            haspopup = active_element.get_attribute("aria-haspopup")
            has_type = tag_name == "button" and haspopup == "listbox"

    if has_type:
        listbox_id = active_element.get_attribute("aria-controls")

        if listbox_id:
            listbox = page.locator(f'[role="listbox"][id="{listbox_id}"]:visible')
        else:
            listbox = page.locator('[role="listbox"]:visible')

        if listbox.count() != 1:
            return False, state

        option_locator = listbox.locator('[role="option"]')
        options = [option.strip() for option in option_locator.all_text_contents()]

        if not options:
            return False, state

    else:
        return False, state

    prompt = f"""
You're an AI Applicant helper in the quick workdays select prompt.

You're job is to look at the current question, the options, and the User Profile to determine out desired option.

Current Question: {current_answer}

Options: {options}

Example Output 1: {{option: 2}}

Example Output 2: {{option: None}}

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

    response = quick_select_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ])

    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)

    answer = response["parsed"]
    desired_option = answer.get("option")

    if not isinstance(desired_option, int) or isinstance(desired_option, bool) or desired_option < 0 or desired_option >= len(options):
        return False, state

    desired_text = options[desired_option]

    if not desired_text:
        return False, state

    try:
        selected_option = option_locator.nth(desired_option)

        if not selected_option.is_visible() or selected_option.get_attribute("aria-disabled") == "true":
            return False, state

        selected_option.click(timeout=3000)

    except Exception:
        return False, state

    complete, state = review_quick_process(current_answer=current_answer, desired_text=desired_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    return complete, state


def quick_greenhouse_select_process(current_answer: dict, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator(":focus")
    has_type = False

    if active_element.count() == 1:
        tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
        role = active_element.get_attribute("role")
        aria_autocomplete = active_element.get_attribute("aria-autocomplete")
        has_type = tag_name == "input" and role == "combobox" and aria_autocomplete == "list"

    if not has_type:
        active_element = page.evaluate_handle("document.activeElement").as_element()

        if active_element:
            tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
            role = active_element.get_attribute("role")
            aria_autocomplete = active_element.get_attribute("aria-autocomplete")
            has_type = tag_name == "input" and role == "combobox" and aria_autocomplete == "list"

    if has_type:
        listbox_id = active_element.get_attribute("aria-controls")

        if not listbox_id:
            return False, state

        listbox = page.locator(f'[role="listbox"][id="{listbox_id}"]:visible')

        if listbox.count() != 1:
            return False, state

        option_locator = listbox.locator('[role="option"]')
        options = [option.strip() for option in option_locator.all_text_contents()]

        if not options:
            return False, state

    else:
        return False, state

    prompt = f"""
You're an AI Applicant helper in the quick workdays select prompt.

You're job is to look at the current question, the options, and the User Profile to determine out desired option.

Current Question: {current_answer}

Options: {options}

Example Output 1: {{option: 2}}

Example Output 2: {{option: None}}

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

    response = quick_select_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ])

    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)

    answer = response["parsed"]
    desired_option = answer.get("option")

    if not isinstance(desired_option, int) or isinstance(desired_option, bool) or desired_option < 0 or desired_option >= len(options):
        return False, state

    desired_text = options[desired_option]

    if not desired_text:
        return False, state

    try:
        selected_option = option_locator.nth(desired_option)

        if not selected_option.is_visible() or selected_option.get_attribute("aria-disabled") == "true":
            return False, state

        selected_option.click(timeout=3000)

    except Exception:
        return False, state

    complete, state = review_quick_process(current_answer=current_answer, desired_text=desired_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    return complete, state


def quick_time_process(current_answer: dict, date_type: str, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator(":focus")
    has_type = False

    if date_type not in ["date", "month"]:
        return False, state

    if active_element.count() == 1:
        tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
        element_type = active_element.get_attribute("type")
        has_type = tag_name == "input" and element_type == date_type

    if not has_type:
        active_element = page.evaluate_handle("document.activeElement").as_element()

        if active_element:
            tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
            element_type = active_element.get_attribute("type")
            has_type = tag_name == "input" and element_type == date_type

    if not has_type:
        return False, state

    prompt = f"""

You're an AI Applicant Helper in the quick time Process.

You're goal in the quick time process is to look at the current question, input type, and user profile to answer the question.

Example response 1

{{

year: 2029,

month: 8,

day: 30

}}

Example response 2

{{

year: 1998,

month: 12,

day: None

}}

Current Question: {current_answer}

Date type: {date_type}

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

    response = quick_time_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ])

    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)

    answer = response["parsed"]
    print(f"quick time answer: {answer}")

    year = answer.get("year")
    month = answer.get("month")
    day = answer.get("day")

    if year is None or month is None:
        return False, state

    try:
        year = int(year)
        month = int(month)

        if date_type == "date":
            if day is None:
                return False, state

            day = int(day)
            desired_text = datetime(year, month, day).strftime("%Y-%m-%d")

        elif date_type == "month":
            desired_text = datetime(year, month, 1).strftime("%Y-%m")

    except (ValueError, TypeError, OverflowError):
        return False, state

    try:
        active_element.fill(desired_text)
    except Exception:
        print("active element filling didn't work")
        return False, state

    complete, state = review_quick_process(current_answer=current_answer, desired_text=desired_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    return complete, state

def adaptive_quick_time_process(current_answer: dict, date_type: str, state: ApplicationState):
    page = state["current_page"]
    prompt = f"""
You're an AI Applicant Helper in the adaptive quick time process.

You will look at the current question, the date_type, and the USER Profile to answer the question.

Current Question: {current_answer}

Date Type: {date_type}

If the date type is year your example response format will be this.

{{
year: 2028
}}

If the date type is month your example response format will be this.

{{
year: 2024
month: 10
}}

If the date type is day your example response format will be this.

{{
year: 2007
month: 14
day: 29
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
    response = quick_time_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    year = answer.get("year")
    month = answer.get("month")
    day = answer.get("day")
    return year, month, day, state
    

def quick_search_process(current_answer: dict, incorrect_searches: list, allowed_multiple_searches: bool, state: ApplicationState):
    page = state["current_page"]["page"]

    prompt = f"""
You're an AI Applicant in the quick search process.

You're job is to look at the current Question and the USER PROFILE to answer the Current question with a list of text as the response

You will also look at the list of incorrect searches so far and then see if we are allowed to give multiple searches or not.


Current Question: {current_answer}

Allowed Multiple Searches: {allowed_multiple_searches}

Incorrect Searches: {incorrect_searches}

Example Response 1: {{list_text: [state]}}

IF we should have multiple searches and we are allowed then you can do something like this.
Example Response 2: {{list_text: [skill 1, skill 2, skill 10]}}

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
    response = quick_search_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    list_text = answer.get("list_text")
    return list_text, state

def quick_smart_recruiters_select_or_search_process(current_answer: dict, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator(":focus")
    has_type = False

    if active_element.count() == 1:
        tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
        input_type = active_element.get_attribute("type")
        role = active_element.get_attribute("role")
        aria_autocomplete = active_element.get_attribute("aria-autocomplete")
        aria_haspopup = active_element.get_attribute("aria-haspopup")
        has_type = tag_name == "input" and input_type == "text" and role == "combobox" and aria_autocomplete in ["list", "both"] and aria_haspopup == "listbox"

    if not has_type:
        active_element = page.evaluate_handle("document.activeElement").as_element()

        if active_element:
            tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
            input_type = active_element.get_attribute("type")
            role = active_element.get_attribute("role")
            aria_autocomplete = active_element.get_attribute("aria-autocomplete")
            aria_haspopup = active_element.get_attribute("aria-haspopup")
            has_type = tag_name == "input" and input_type == "text" and role == "combobox" and aria_autocomplete in ["list", "both"] and aria_haspopup == "listbox"

    if not has_type:
        return False, state

    dropdown_script = """
    (element) => {
        let current = element;

        while (current) {
            if (current.tagName?.toLowerCase() === "spl-dropdown") {
                return current;
            }

            current = current.parentElement || current.getRootNode()?.host;
        }

        return null;
    }
    """

    dropdown_handle = active_element.evaluate_handle(dropdown_script)
    dropdown = dropdown_handle.as_element()

    if not dropdown:
        return False, state

    option_script = """
    (element) => {
        function findOptions(root) {
            let options = [...root.querySelectorAll("spl-select-option")];

            for (const child of root.querySelectorAll("*")) {
                if (child.shadowRoot) {
                    options.push(...findOptions(child.shadowRoot));
                }
            }

            return options;
        }

        return findOptions(element).map((option, index) => ({
            index: index,
            value: option.getAttribute("value"),
            text: option.textContent.trim(),
            disabled: option.hasAttribute("disabled")
        }));
    }
    """

    click_script = """
    (element, desiredIndex) => {
        function findOptions(root) {
            let options = [...root.querySelectorAll("spl-select-option")];

            for (const child of root.querySelectorAll("*")) {
                if (child.shadowRoot) {
                    options.push(...findOptions(child.shadowRoot));
                }
            }

            return options;
        }

        const options = findOptions(element);
        const option = options[desiredIndex];

        if (!option || option.hasAttribute("disabled")) {
            return false;
        }

        option.click();
        return true;
    }
    """

    def get_options():
        all_options = dropdown.evaluate(option_script)
        return [option for option in all_options if option["value"] != "#spl-custom-option" and option["text"] and not option["disabled"]]

    options = get_options()
    incorrect_searches = []

    for attempt in range(3):
        if options:
            break

        list_text, state = quick_search_process(current_answer=current_answer, incorrect_searches=incorrect_searches, allowed_multiple_searches=False, state=state)

        if not isinstance(list_text, list) or len(list_text) != 1:
            return False, state

        search_text = str(list_text[0]).strip()

        if not search_text or search_text.lower() in [str(search).lower() for search in incorrect_searches]:
            return False, state

        active_element.fill("")
        page.keyboard.type(search_text)
        page.wait_for_timeout(500)

        options = get_options()

        if not options:
            incorrect_searches.append(search_text)

    if not options:
        return False, state

    total_options = [option["text"] for option in options]

    desired_option, state = adaptive_select_process(current_answer=current_answer, total_options=total_options, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    if not isinstance(desired_option, int) or isinstance(desired_option, bool) or not 0 <= desired_option < len(options):
        return False, state

    desired_text = options[desired_option]["text"]
    desired_index = options[desired_option]["index"]

    clicked = dropdown.evaluate(click_script, desired_index)

    if not clicked:
        return False, state

    complete, state = review_quick_process(current_answer=current_answer, desired_text=desired_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    return complete, state

from datetime import date

def quick_smart_recruiters_time_process(current_answer: list, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]

    # First method: Playwright focused element.
    active_element = page.locator(":focus")
    has_type = False

    check_script = """
    (element) => {
        return element.tagName.toLowerCase() === "input"
            && element.type === "text"
            && element.hasAttribute("data-input")
            && element.classList.contains("flatpickr-input")
            && element.getAttribute("aria-haspopup") === "grid";
    }
    """

    if active_element.count() == 1:
        has_type = active_element.evaluate(check_script)

    # Second method: Deep focus through Shadow DOM.
    if not has_type:
        focus_script = """
        () => {
            let active = document.activeElement;

            while (active?.shadowRoot?.activeElement) {
                active = active.shadowRoot.activeElement;
            }

            return active;
        }
        """

        active_element = page.evaluate_handle(focus_script).as_element()

        if active_element:
            has_type = active_element.evaluate(check_script)

    if not has_type:
        return False, state

    # Locate the Flatpickr instance and inspect its configuration.
    flatpickr_script = """
    (element) => {
        let current = element;

        while (current) {
            if (current._flatpickr) {
                const fp = current._flatpickr;

                return {
                    found: true,
                    date_format: fp.config.dateFormat,
                    alt_format: fp.config.altFormat,
                    enable_time: fp.config.enableTime,
                    month_picker: !!fp.config.plugins?.some(plugin => String(plugin).includes("monthSelect"))
                };
            }

            current = current.parentElement || current.getRootNode()?.host;
        }

        return {found: false};
    }
    """

    flatpickr_details = active_element.evaluate(flatpickr_script)

    if not flatpickr_details["found"]:
        return False, state

    # Determine which date components the field expects.
    date_format = flatpickr_details.get("date_format") or ""
    alt_format = flatpickr_details.get("alt_format") or ""

    if flatpickr_details.get("month_picker"):
        date_type = "month"
    elif "d" in date_format or "j" in date_format:
        date_type = "day"
    elif any(token in date_format for token in ["m", "n", "M", "F"]):
        date_type = "month"
    elif "Y" in date_format or "y" in date_format:
        date_type = "year"
    elif "d" in alt_format or "j" in alt_format:
        date_type = "day"
    else:
        date_type = "month"

    # Ask the LLM to determine the appropriate date.
    year, month, day, state = adaptive_quick_time_process(current_answer=current_answer, date_type=date_type, state=state)

    # Validate and construct a complete date for Flatpickr.
    try:
        year = int(year)

        if date_type == "year":
            month = 1
            day = 1

        elif date_type == "month":
            month = int(month)
            day = 1

        else:
            month = int(month)
            day = int(day)

        selected_date = date(year, month, day)
        date_value = selected_date.strftime("%Y-%m-%d")

    except (TypeError, ValueError, OverflowError):
        return False, state

    # Set the date using the Flatpickr instance.
    set_date_script = """
    (element, dateValue) => {
        let current = element;

        while (current) {
            if (current._flatpickr) {
                const fp = current._flatpickr;

                fp.setDate(dateValue, true, "Y-m-d");

                return {
                    success: fp.selectedDates.length > 0,
                    value: element.value
                };
            }

            current = current.parentElement || current.getRootNode()?.host;
        }

        return {success: false, value: null};
    }
    """

    result = active_element.evaluate(set_date_script, date_value)

    if not result["success"]:
        return False, state

    # Once the date is set, immediately review and return.
    complete, state = review_quick_process(current_answer=current_answer, desired_text=result["value"], old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

    return complete, state

def adaptive_quick_icims_select_process(current_answer: list, total_options: list[str], incorrect_searches: list, searchable: bool, state: ApplicationState):
    page = state["current_page"]["page"]
    prompt = f"""
You're an AI Applicant Helper in the adaptive quick select process.

You will look at the current question, total options, and user profile, and need to determine if any of the options answer the question based on the user profile.

Current Question: {current_answer}

total_options: {total_options}

Incorrect Searches: {incorrect_searches}

Searchable: {searchable}

If any of the options answer the question based off the user profile you will return something like this or if Searchable is False then we must choose one of the options that best answer the question.

Ex: {{desired_option: 20}}

If none of the options answer the current question then we need to search for our own option.

The search must be one word that has the best chance at finding it in a search based process.

Also look at the incorrect searches to make sure you don't search the same thing again.

Ex: {{list_text: [skill 10]}}

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
    response = quick_select_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    desired_option = answer.get("desired_option")
    list_text = answer.get("list_text")
    return desired_option, list_text, state

def quick_icimis_select_or_search_process(current_answer: list, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]

    # First method: Find the focused element through Playwright.
    active_element = page.locator(":focus")
    has_type = False

    check_script = """
    (element) => {
        return element.matches("input.dropdown-search, span.dropdown-text, .dropdown-container, .icimsDropdown, .dropdown-results, li.dropdown-result")
            || !!element.closest(".dropdown-container, .icimsDropdown, .dropdown-results");
    }
    """

    if active_element.count() == 1:
        has_type = active_element.evaluate(check_script)

    # Second method: Find the deeply focused element.
    if not has_type:
        focus_script = """
        () => {
            let active = document.activeElement;

            while (active?.shadowRoot?.activeElement) {
                active = active.shadowRoot.activeElement;
            }

            return active;
        }
        """

        active_element = page.evaluate_handle(focus_script).as_element()

        if active_element:
            has_type = active_element.evaluate(check_script)

    # Find the currently visible iCIMS dropdown.
    dropdown_script = """
    () => {
        const results = [...document.querySelectorAll("ul.dropdown-results")]
            .find(element => {
                const style = getComputedStyle(element);

                return element.getClientRects().length > 0
                    && style.visibility !== "hidden"
                    && style.display !== "none";
            });

        if (!results) return null;

        const searchInput = [...document.querySelectorAll("input.dropdown-search")]
            .find(input => {
                const style = getComputedStyle(input);

                return input.getAttribute("aria-controls") === results.id
                    && input.getClientRects().length > 0
                    && style.visibility !== "hidden"
                    && style.display !== "none";
            });

        return {
            results_id: results.id,
            searchable: !!searchInput
        };
    }
    """

    dropdown_details = page.evaluate(dropdown_script)

    if not dropdown_details:
        return False, state

    results_id = dropdown_details["results_id"]
    searchable = dropdown_details["searchable"]

    # Retrieve all available options from the active dropdown.
    options_script = """
    (resultsId) => {
        const results = document.getElementById(resultsId);

        if (!results) return [];

        return [...results.querySelectorAll("li.dropdown-result.result-selectable")]
            .filter(element => {
                const style = getComputedStyle(element);

                return element.getClientRects().length > 0
                    && style.visibility !== "hidden"
                    && style.display !== "none";
            })
            .map(element => ({
                text: element.textContent.trim(),
                id: element.id
            }));
    }
    """

    incorrect_searches = []

    # Initial evaluation + maximum of 3 searches.
    for attempt in range(4):
        time.sleep(5)

        options = page.evaluate(options_script, results_id)
        total_options = [option["text"] for option in options]

        if not total_options and not searchable:
            return False, state

        desired_option, list_text, state = adaptive_quick_icims_select_process(current_answer=current_answer, total_options=total_options, incorrect_searches=incorrect_searches, searchable=searchable, state=state)

        # Select one of the available options.
        if desired_option is not None:
            try:
                desired_option = int(desired_option)
            except (TypeError, ValueError):
                return False, state

            if not 0 <= desired_option < len(options):
                return False, state

            selected_option = options[desired_option]
            desired_text = selected_option["text"]
            option_id = selected_option["id"]

            clicked = page.evaluate("""
            ({resultsId, optionId, desiredText}) => {
                const results = document.getElementById(resultsId);
                const option = document.getElementById(optionId);

                if (!results || !option || !results.contains(option)) return false;
                if (option.textContent.trim() !== desiredText) return false;

                option.click();
                return true;
            }
            """, {"resultsId": results_id, "optionId": option_id, "desiredText": desired_text})

            if not clicked:
                return False, state

            complete, state = review_quick_process(current_answer=current_answer, desired_text=desired_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

            return complete, state

        # Stop if searching is unavailable or all 3 searches have been used.
        if not searchable or attempt == 3:
            return False, state

        if not isinstance(list_text, list) or not list_text:
            return False, state

        search_text = str(list_text[0]).strip().lower()

        if not search_text or search_text in incorrect_searches:
            return False, state

        # Clear the current search using keyboard actions.
        for i in range(1000):
            page.keyboard.press("ArrowRight")

        for i in range(1000):
            page.keyboard.press("Backspace")

        # Type the new search term.
        page.keyboard.type(search_text)

        incorrect_searches.append(search_text)

    return False, state

def review_quick_process(current_answer: list, desired_text: str, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    if full_page_height == old_page_height:
        encoded_bytes, cut_off_bottom_height, cut_off_top_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=encoded_bytes)
    else:
        encoded_bytes, cut_off_bottom_height, cut_off_top_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=encoded_bytes, boxes_details2=old_boxes_details, full_page_width=full_page_width, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)
    encoded_bytes, boxes_details = expand_image(encoded_bytes=encoded_bytes)

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

You're an AI Applicant Helper in the review quick process.

Current Question: {current_answer}

Desired Answer: {desired_text}

You have to look at the current question and it's if answer, if there is no answer or the answer is incorrect to the desired text stop and return.
- {{“action”: None, complete: False}}

If the answer is correctly answered follow this subprocess.

If the image does not have some exit button to leave the current question then return this.
{{action: white_pixel, icon: -1, complete: True}} 

Page Elements Format:
[icon, type, coordinates, content]

Page Elements: {page_elements}

If the image does have some exit button to leave the current question then return something like this.
- look at the image and the Page Elements to find the icon to click to exit.
- {{action: click, icon: 8, complete: True}}

"""

    response = review_quick_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
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
    new_tokens, model_name = details_process(details=details)

    state = ai_token_tracker(
        new_tokens=new_tokens,
        model_name=model_name,
        state=state
    )

    answer = response["parsed"]
    print(f"review quick answer: {answer}")

    action = answer.get("action")
    icon = answer.get("icon")
    complete = answer.get("complete")

    if not action:
        return False, state

    context = state.get("context")
    page_count = len(context.pages)

    if action == "white_pixel":
        state = execute_action(
            current_answer=["white_pixel", -1],
            current_box=-1,
            full_page_width=full_page_width,
            full_page_height=full_page_height,
            page_count=page_count,
            state=state
        )

        return True, state

    if action == "click":
        if (
            not isinstance(icon, int)
            or isinstance(icon, bool)
            or icon < 0
            or icon >= len(boxes_details)
        ):
            return False, state

        current_box = boxes_details[icon]

        state = execute_action(
            current_answer=["click", icon],
            current_box=current_box,
            full_page_width=full_page_width,
            full_page_height=full_page_height,
            page_count=page_count,
            state=state
        )
        return True, state

    return False, state

def workday_select_options(state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator(":focus")

    if active_element.count() != 1:
        return []

    tag_name = active_element.evaluate("(element) => element.tagName.toLowerCase()")
    haspopup = active_element.get_attribute("aria-haspopup")

    if tag_name == "button" and haspopup == "listbox":
        listbox_id = active_element.get_attribute("aria-controls")

        if listbox_id:
            listbox = page.locator(f'[role="listbox"][id="{listbox_id}"]:visible')
        else:
            listbox = page.locator('[role="listbox"]:visible')

        if listbox.count() != 1:
            return []

        options = listbox.locator('[role="option"]').all_text_contents()

        return [option.strip() for option in options if option.strip()]

    return []

def extra_steps_process(current_answer: list, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_width: int, old_page_height: int, cut_off_height: int, page_x: int, page_y: int, state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator(":focus")

    select_tag = False
    date_type = None

    # First method: locator(":focus")

    if active_element.count() > 0:
        select_tag = active_element.evaluate("(el) => el.tagName.toLowerCase() === 'select'")

        input_type = active_element.get_attribute("type")

        if input_type in ["date", "month"]:
            date_type = input_type

    # Second method: document.activeElement
    if not select_tag and date_type is None:
        active_element = page.evaluate_handle("document.activeElement").as_element()


        if active_element is not None:
            select_tag = active_element.evaluate("(el) => el.tagName.toLowerCase() === 'select'")

            input_type = active_element.get_attribute("type")

            if input_type in ["date", "month"]:
                date_type = input_type

    # Quick select process
    if select_tag:
        print("going through quick select")

        complete, state = quick_select_process(current_answer=current_answer, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

        if complete:
            return state

    # Quick time process
    elif date_type is not None:
        print(f"going through quick time process: {date_type}")

        complete, state = quick_time_process(current_answer=current_answer, date_type=date_type, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)

        if complete:
            return state
    pyautogui_image = pyautogui.screenshot(region=(10, 40, old_page_width, 910))
    buffer = io.BytesIO()
    pyautogui_image.save(buffer, format="PNG")
    pyautogui_bytes = buffer.getvalue()
    encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    data = response.json()
    pyautogui_encoded_bytes = data["encoded_bytes"]
    boxes_details = data["boxes_details"]
    pyautogui_encoded_bytes = boxes_only_process(encoded_bytes=pyautogui_encoded_bytes, boxes_details=boxes_details)
    do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    desired = boxes_details[4]
    bbox = desired["bbox"]
    page_x, page_y = coordinates_process(coordinates=bbox, full_page_width=full_page_width, full_page_height=full_page_height)
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
    if current_height == old_page_height:
        print("used pixel image cropping in extra steps")
        encoded_bytes, min_cut_off_height, max_cut_off_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=encoded_bytes)
    else:
        print("used cropped image process in extra steps")
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes, min_cut_off_height, max_cut_off_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=encoded_bytes, boxes_details2=boxes_details, cut_off_height=cut_off_height, full_page_width=full_page_width, old_page_height=old_page_height, state=state)
    encoded_bytes, boxes_details, do_not_use1, do_not_use2 = omniparser_process(encoded_bytes=encoded_bytes, state=state)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    # image.show()
    comparison_page_width2, comparison_page_height2 = image.size
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 0), round(bbox[1], 0), round(bbox[2], 0), round(bbox[3], 0)]
        content = current_box["content"]
        page_elements.append([icon, coordinates, content])
    prompt = f"""
You're an AI Applicant in the Extra Step Process with only looking at the current question.

You will only be looking at the current question during this process.

Current Question + guidance to answering the question: {current_answer}



PAGE ELEMENTS FORMAT
[icon, coordinates, content]

Page Elements: {page_elements}

For any icon clicking you will use the page elements from image1 to answer.

You will Follow the Extra Steps Process to complete this question.

Extra Steps Process

1. First you need to determine what type of action we will be taking and the options you have are, dropdown, search, and time.
    - dropdown: if you see options for the current question that means we are using the dropdown action.
    - Search: If there're no options available for the current question and this is not a time question that means we are using the search action.
    - Time: If you see for the current question that there is no options and it is a time question we will be using the time action.

How to handle each action.

How to Handle dropdown Action

1. First look at the body text and the image and find all the options for the current question
2. Determine if you can click the option you want to click look at the page elements in image 1. If you can stop and return something like this.
    - You need to find the right icon to click, then list the current_option (usually the highlighted option in the photo or it's just the first option/dropdown option), desired_option, total_options, current_text, and desired_text, determine if image1 has options, determine if image2 has options, and what is the exact current question.
    - Ex: {{action: dropdown, dropdown_type: click, icon: 19, current_option: 5, desired_option: 8, total_options: 10, current_text: maybe, desired_text: yes, image1: True, image2: False, current_question: What state are you from?}}
3. If you can't click the icon that is available then you need to find the current_option that we are on in the image, then find the option number that we want to go to, return something like this.
    - You need to find the current_option (usually the highlighted option in the photo or it's just the first option/dropdown option), the desired_option, the total_options available, the first_text (the first option), and the desired_text, determine if image1 has options, determine if image2 has options, and what is the exact current question.
    - Ex: {{action: dropdown, dropdown_type: arrow, current_option: 12, desired_option: 5, total_options: 24, current_text: Alabama, desired_text: example, image1: True, image2: True, current_question: What city are you from?}}

How to Handle the search Action

1. First look at the current question and the USER PROFILE and decide what is the best way to answer this, with the highest likelihood that a suggestion pops up for the answer.
2. Some Search Action will need a list of answers and some will just need one individual answer. Your job is to look at the current question and the USER PROFILE to be able to determine if it is a single word type of response or is it multiple single word responses need to be inputed, you also need to find the exact current question.
    - Ex 1: {{action: search, list_text: [college], current_question: What university did you attend?}}
    - Ex 2: {{action: search, list_text: [skill 1, skill 2, skill 3], What skills do you have?}}

How to Handle the time Action:
If the Time has dropdown options, go back up to the dropdown subprocess and choose that.
If the time has a calendar popup is the only time you follow the calendar process.

Do not choose the Time action if it doesn't have a calendar popup.
1. First look at the current question and the format for the question and then the USER PROFILE and determine what the desired_date should be.
2. Determine how many arrows to the left do we need to be to be at the farthest point to the left of the current question.
3. Next determine which images have the calendar popup, image1 and image2 can both be true and false
4. The desired_date must be in numbers format and should match the format the question is asking for,
5. You need to find the exact current question.
    - day format ex: {{action: time, desired_date: 08/25/26, left_arrow: 0, image1: True, image2: False, current_question: When could you start working at this job?}}
    - month format ex: {{action: time, desired_date: 08/26, left_arrow: 2, image1: False, image2: False, current_question: When will you graduate college?}}
    - Year format ex: {{action: time, desired_date: 2026, left_arrow: 1, image1: True, image2: True, current_question: When did you start your first job?}}

Actions Descriptions

dropdown - When the current question has options and we don't need to search/input any text always choose the dropdown option.

search - When the current question has no options and is not a time question choose the search search action.

time - You only choose the time action when you see Time AND a CALENDAR Popup.

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

    response = extra_steps_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{pyautogui_encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    print(f"extra steps answer: {answer}")
    action = answer.get("action")
    action_type = answer.get("action_type")
    icon = answer.get("icon")
    current_option = answer.get("current_option")
    desired_option = answer.get("desired_option")
    total_options = answer.get("total_options")
    first_text = answer.get("first_text")
    desired_text = answer.get("desired_text")
    list_text = answer.get("list_text")
    desired_date = answer.get("desired_date")
    left_arrow = answer.get("left_arrow")
    image1 = answer.get("image1")
    image2 = answer.get("image2")
    current_question = answer.get("current_question")
    if current_question is not None:
        current_answer[-1] = current_question
    print(f"current answer in extra steps: {current_answer}")
    if action == "dropdown":
        if action_type == "arrow":
            print("going to arrow process")
            print(f"current_option: {current_option}, desired_option: {desired_option}")
            if current_option is not None and desired_option is not None:
                print("made it to the real arrow")
                new_answer = ["arrow", current_option, desired_option]
                page_count = len(state.get("context").pages)
                state = execute_action(current_answer=new_answer, current_box=-1, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
        if action_type == "click":
            context = state.get("context")
            page_count = len(context.pages)
            new_answer = ["click", icon]
            current_box = boxes_details[icon]
            current_bbox = current_box["bbox"]
            if min_cut_off_height is None or max_cut_off_height is None:
                new_page_height = full_page_height
            else:
                new_page_height = max_cut_off_height - min_cut_off_height
            desired_box = cropped_coordinates_process(min_cut_off_height=min_cut_off_height, full_page_height1=full_page_height, full_page_height2=new_page_height, desired_bbox=current_bbox)
            current_box["bbox"] = desired_box
            middle_x, middle_y = coordinates_process(coordinates=desired_box, full_page_width=full_page_width, full_page_height=full_page_height)
            print("---------------------------------------------------------------------------------------------")
            pyautogui.moveTo(middle_x * full_page_width, middle_y * full_page_height)
            time.sleep(5)
            state = execute_action(current_answer=new_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
        print("going to dropdown process")
        state = dropdown_process(current_answer=current_answer, previous_action=action_type, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, page_x=page_x, page_y=page_y, first_text=first_text, desired_text=desired_text, desired_option=desired_option, total_options=total_options, image1=image1, image2=image2, state=state)
    elif action == "search":
        state = search_process(current_answer=current_answer, list_text=list_text, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, old_x=page_x, old_y=page_y, state=state)
    elif action == "time":
        state = time_process(current_answer=current_answer, desired_date=desired_date, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, full_page_width=full_page_width, page_x=page_x, page_y=page_y, image1=image1, image2=image2, state=state)
    return state

def extra_steps_action(current_answer: list, full_page_width: int, full_page_height: int, state: ApplicationState, boxes_details=None):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details = expand_image(encoded_bytes=encoded_bytes)
    context = state.get("context")
    page_count = len(context.pages)
    action = current_answer[0]
    if action == "dropdown":
        action_type = current_answer[1]
        if action_type == "click":
            icon = current_answer[2]
            current_box = boxes_details[icon]
            current_answer = [action_type, icon]
            print("markdown action in extra steps")
            state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
            state = dropdown_process()
            return state
        else:
            current_answer
    elif action == "search":
        print("search action in extra steps")
    elif action == "time":
        print("time action in extra steps")

def normalize_text(content: str):
    if isinstance(content, str):
        return "".join(char.lower() for char in content if char.isalnum())
    else:
        ""

def compare_text(text1: str, text2: str, max_difference: int = 3) -> bool:
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if abs(len(text1) - len(text2)) > max_difference:
        return False

    previous = list(range(len(text2) + 1))

    for i, char1 in enumerate(text1, 1):
        current = [i]

        for j, char2 in enumerate(text2, 1):
            cost = 0 if char1 == char2 else 1

            current.append(min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + cost
            ))

        if min(current) > max_difference:
            return False

        previous = current

    return previous[-1] <= max_difference

def setup_scroll_process(current_answer: list[str], old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, first_text: str, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    first_text = normalize_text(first_text)
    current_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight); }""")
    """decoded_bytes = base64.b64decode(old_encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image.show()"""
    print("-----------------------------------------------------------------------------------------------")
    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    if current_height == old_page_height:
        print("went down pixel route")
        encoded_bytes1, min_cut_height, max_cut_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=encoded_bytes)
    else:
        print("went down cropped route")
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes1, min_cut_height, max_cut_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=encoded_bytes, boxes_details2=boxes_details, cut_off_height=cut_off_height, full_page_width=full_page_width, old_page_height=old_page_height, state=state)
    encoded_bytes, boxes_details, do_not_use, do_not_use2 = omniparser_process(encoded_bytes=encoded_bytes1, state=state)
    decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
    buffer = io.BytesIO(decoded_bytes)
    image = Image.open(buffer)
    image.show()
    print("-----------------------------------------------------------------------------------------------")
    time.sleep(10)
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        current_icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        page_elements.append([current_icon, box_type, coordinates, content])
    print(f"page elements: {page_elements}")
    print(f"first text in setup: {first_text}")
    prompt = f"""
You're an AI Applicant helper and your job is to look at the image and the page elements to find the first option for the current question.
Look at the image and find the current question.

Current Question: {current_answer}

If there are options open for the current question then do no have the action be no_icon.

no_icon: when there are no options/dropdown options for the current question
icon: when there are options/dropdown options for the current questions

We are looking for either the first text or the first option for the current question

First Text: {first_text}

There is a world for the current question there are no options available and we would also return this.
- Return this: {{action: no_icon, icon: None, reason: whatever your reason is}}

Page Elements Format
[icon, type, coordinates, content]

Page Elements: {page_elements}

Example Output 1:
{{action: get_icon, "icon": [1], reason: whatever your reason is}}

Example Output 2:
{{action: get_icon, "icon": [3, 8, 10], reason: whatever your reason is}}
"""
    response = setup_select_process_llm2.invoke([
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}
                }
            ]
        }
    ])

    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(
        new_tokens=new_tokens,
        model_name=model_name,
        state=state
    )
    first_text = ""
    answer = response["parsed"]
    print(f"setup scroll answer: {answer}")
    action = answer.get("action")
    if action == "no_icon":
        print("returnin none for a bunch of items")
        return None, None, None, None, None, None, None, None, action, state
    icon = answer.get("icon")
    if not icon:
        return None, None, None, None, None, None, None, None, action, state
    for i in range(len(icon)):
        current_icon = icon[i]
        current_box = boxes_details[current_icon]
        content = current_box["content"]
        content = normalize_text(content)
        first_text += content

    current_box = boxes_details[icon[-1]]
    zero_coordinate = min(boxes_details[i]["bbox"][0] for i in icon)
    width_pixel = zero_coordinate * full_page_width
    safe_x = [math.floor(width_pixel)-3, math.ceil(width_pixel)+3]
    third_coordinate = max(boxes_details[i]["bbox"][3] for i in icon)
    safe_elements = []
    banned_options = []
    first_option = boxes_details[icon[0]]
    safe_y_axis = min(boxes_details[i]["bbox"][1] for i in icon)
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        current_zero_coordinate = current_box["bbox"][0]
        current_width_pixel = current_zero_coordinate * full_page_width
        content = current_box["content"]
        if content is not None:
            content = normalize_text(content)
            if current_width_pixel >= safe_x[0] and current_width_pixel <= safe_x[1]:
                current_third_coordinate = current_box["bbox"][3]
                if current_third_coordinate < safe_y_axis:
                    banned_options.append(content)
                else:
                    safe_elements.append(current_box)
            else:
                banned_options.append(content)

    closest_elements = []
    for i in range(len(safe_elements)):
        current_box = safe_elements[i]
        if current_box["bbox"][1] > third_coordinate:
            closest_elements.append(current_box)
    closest_elements.sort(key=lambda current_box: current_box["bbox"][1])
    if not closest_elements:
        print("returning none due to there not being a close element")
        return None, None, None, None, None, None, None, None, "no_icon", state
    closest_element = closest_elements[0]
    image_height = max_cut_height - min_cut_height
    scrolling = abs((closest_element["bbox"][1] - third_coordinate)) * image_height
    safe_y = [math.floor(scrolling)-3, math.ceil(scrolling)+3]
    options = []

    first_x_coord = (
        min(boxes_details[i]["bbox"][0] for i in icon)
        + max(boxes_details[i]["bbox"][2] for i in icon)
    ) / 2 * full_page_width

    first_y_coord = (
        min(boxes_details[i]["bbox"][1] for i in icon)
        + max(boxes_details[i]["bbox"][3] for i in icon)
    ) / 2 * image_height + min_cut_height
    print(f"safe_x: {safe_x}, safe_y: {safe_y}, scrolling: {scrolling}, options: {options}, banned options: {banned_options}, first text: {first_text}, first_x_coord: {first_x_coord}, first_y_coord: {first_y_coord}, action: {action}")
    return safe_x, safe_y, scrolling, options, banned_options, first_text, first_x_coord, first_y_coord, action, state

def complete_scroll_process(old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, safe_x: list[int], safe_y: list[int], scrolling: float, options: list, banned_options: list[str], first_text: str, first_x_coord: int, first_y_coord: int, desired_text: str, total_options: int, desired_option: int, move_down: bool, state: ApplicationState):
    page = state["current_page"]["page"]
    comparison_bytes, full_page_width, full_page_height = screenshot_process(state=state)
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")

    if old_page_height == full_page_height:
        encoded_bytes, min_cut_off_height, max_cut_off_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=comparison_bytes)
    else:
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        encoded_bytes, min_cut_off_height, max_cut_off_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=comparison_bytes, boxes_details2=boxes_details, cut_off_height=cut_off_height, old_page_height=old_page_height, full_page_width=full_page_width, state=state)
    
    encoded_bytes, boxes_details, do_not_use, do_not_use2 = omniparser_process(encoded_bytes=encoded_bytes, state=state)
    desired_text = normalize_text(desired_text)
    first_text = normalize_text(first_text)
    banned_options = [normalize_text(content) for content in banned_options]

    reorganized_elements = []
    image_height = max_cut_off_height - min_cut_off_height
    for i in range(len(boxes_details)):
        current_box = boxes_details[i].copy()
        print(f"current box content: {current_box["content"]}")
        current_x_axis = current_box["bbox"][0] * full_page_width

        if current_x_axis < safe_x[0] or current_x_axis > safe_x[1]:
            continue
        
        content = normalize_text(current_box["content"])

        if not content or content in banned_options:
            continue
        print("got through both filters")
        current_box["content"] = content
        if content == desired_text:
            current_x = (current_box["bbox"][0] + current_box["bbox"][2]) / 2
            current_y = (current_box["bbox"][1] + current_box["bbox"][3]) / 2

            current_x *= full_page_width
            current_y = (image_height * current_y) + min_cut_off_height
            print("we are clicking with current text = desired text")
            print(f"current element: {current_box}")
            print(f"complete x: {current_x}, complete y: {current_y}")
            page.mouse.click(current_x, current_y)

            return True, options, comparison_bytes, state
        reorganized_elements.append(current_box)

    reorganized_elements.sort(key=lambda current_box: current_box["bbox"][1])

    combined_elements = []

    if reorganized_elements:
        combined_elements.append(reorganized_elements[0])

        for i in range(1, len(reorganized_elements)):
            current_box = reorganized_elements[i]
            recent_box = combined_elements[-1]

            current_content = current_box["content"]
            recent_content = recent_box["content"]

            recent_y_axis = recent_box["bbox"][3]
            current_y_axis = current_box["bbox"][1]

            y_axis_difference = (current_y_axis - recent_y_axis) * image_height

            if y_axis_difference > safe_y[1]:
                break

            elif y_axis_difference >= safe_y[0]:
                combined_elements.append(current_box)

            else:
                content = recent_content + current_content

                zero_coordinate = min(current_box["bbox"][0], recent_box["bbox"][0])
                first_coordinate = min(current_box["bbox"][1], recent_box["bbox"][1])
                second_coordinate = max(current_box["bbox"][2], recent_box["bbox"][2])
                third_coordinate = max(current_box["bbox"][3], recent_box["bbox"][3])

                bbox = [zero_coordinate, first_coordinate, second_coordinate, third_coordinate]

                data = {
                    "icon": recent_box["icon"],
                    "type": "text",
                    "bbox": bbox,
                    "content": content,
                }

                combined_elements[-1] = data

    while combined_elements:
        current_content = combined_elements[0]["content"]

        if any(
            current_content == old_box["content"]
            or current_content in old_box["content"]
            for old_box in options
        ):
            combined_elements.pop(0)
        else:
            break
    # Only remove the final element from the new scan.
    if combined_elements:
        last_element = combined_elements[-1]
        last_content = normalize_text(last_element["content"])

        if last_content != desired_text and len(options) + len(combined_elements) < total_options:
            combined_elements.pop()
            
    # Keep all previous options and append the new ones.
    old_options_length = len(options)
    if len(combined_elements) > 0:
        options.extend(combined_elements)

    # First check for an exact text match.
    for i in range(old_options_length, len(options)):
        current_element = options[i]
        current_text = normalize_text(current_element["content"])

        if current_text == desired_text:
            current_x = (current_element["bbox"][0] + current_element["bbox"][2]) / 2
            current_y = (current_element["bbox"][1] + current_element["bbox"][3]) / 2

            current_x *= full_page_width
            current_y = (image_height * current_y) + min_cut_off_height
            print("we are clicking with current text = desired text")
            print(f"current element: {current_element}")
            page.mouse.click(current_x, current_y)

            return True, options, comparison_bytes, state
        if i == desired_option:
            desired_option_correct = compare_text(text1=desired_text, text2=current_text)
            if desired_option_correct:
                current_x = (current_element["bbox"][0] + current_element["bbox"][2]) / 2
                current_y = (current_element["bbox"][1] + current_element["bbox"][3]) / 2

                current_x *= full_page_width
                current_y = (image_height * current_y) + min_cut_off_height
                print("we are clicking because i == desired option")
                print(f"current element: {current_element}")
                page.mouse.click(current_x, current_y)

                return True, options, comparison_bytes, state

    if len(combined_elements) > 0:
        print("used last element in the combined elements")
        first_element = combined_elements[0]
        last_element = combined_elements[-1]

        first_x = (first_element["bbox"][0] + first_element["bbox"][2]) / 2
        first_y = (first_element["bbox"][1] + first_element["bbox"][3]) / 2

        last_x = (last_element["bbox"][0] + last_element["bbox"][2]) / 2
        last_y = (last_element["bbox"][1] + last_element["bbox"][3]) / 2

        current_x = ((first_x + last_x) / 2) * full_page_width
        current_y = ((first_y + last_y) / 2) * image_height + min_cut_off_height

        page.mouse.move(current_x, current_y)
        """elif len(options) > 0:
        last_element = options[-1]
        print(f"last element: {last_element}")
        last_x = (last_element["bbox"][0] + last_element["bbox"][2]) / 2
        last_y = (last_element["bbox"][1] + last_element["bbox"][3]) / 2
        page.mouse.move(last_x, last_y"""
    else:
        print("used first element")
        page.mouse.move(first_x_coord, first_y_coord)
    if move_down == True:
        page.mouse.wheel(0, scrolling * 3)
    else:
        page.mouse.wheel(0, -(scrolling * 3))
    print(f"combined elements: {combined_elements}")
    return False, options, comparison_bytes, state    


def scroll_process(current_answer: dict, old_encoded_bytes: str, old_boxes_details: list[dict], old_x: int, old_y: int, old_page_width: int, old_page_height: int, cut_off_height: int, first_text: str, desired_text: str, total_options: int, desired_option: int, move_down: bool, state: ApplicationState):
    page = state["current_page"]["page"]
    print("pre setup")
    print(f"scrol first text: {first_text}")
    safe_x, safe_y, scrolling, options, banned_options, new_first_text, first_x_coord, first_y_coord, action, state = setup_scroll_process(current_answer=current_answer, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, first_text=first_text, state=state)
    print("got through set up")
    if action == "no_icon" or not action or safe_x is None:
        current_height = page.evaluate("""() => { return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight)}""")
        if current_height == old_page_height:
            page.mouse.click(old_x, old_y)
        else:
            page_x, page_y, state = find_icon(current_answer=current_answer, state=state)
            page.mouse.click(page_x, page_y)
        safe_x, safe_y, scrolling, options, banned_options, new_first_text, first_x_coord, first_y_coord, action, state = setup_scroll_process(current_answer=current_answer, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, first_text=first_text, state=state)
        if action == "no_icon" or not action:
            return state

    same_bytes_tracker = 0
    old_bytes = []
    for i in range(total_options * 3):
        print(f"we are iteration: {i} of the complete scroll process")
        complete, options, new_encoded_bytes, state = complete_scroll_process(old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, safe_x=safe_x, safe_y=safe_y, scrolling=scrolling, options=options, banned_options=banned_options, first_text=new_first_text, first_x_coord=first_x_coord, first_y_coord=first_y_coord, desired_text=desired_text, total_options=total_options, desired_option=desired_option, move_down=move_down, state=state)
        if complete:
            break
        if i == 0:
            old_bytes.append(new_encoded_bytes)
            continue
        else:
            comparison_byte = old_bytes[-1]
            if compare_pixel(encoded_bytes1=comparison_byte, encoded_bytes2=new_encoded_bytes):
                same_bytes_tracker += 1
            else:
                same_bytes_tracker = 0
            if same_bytes_tracker >= 2:
                print("same page twice and we need to leave")
                break
            old_bytes.append(new_encoded_bytes)
    return state

def time_process(current_answer: str, desired_date: str, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, full_page_width: int, page_x: int, page_y: int, image1: bool, image2: bool, state: ApplicationState):
    page = state["current_page"]["page"]
    """state, desired_date, image1, image2 = text_time_process(current_question=current_question, full_page_width=full_page_width, state=state)
    has_type = False
    active_element = page.locator(":focus")
    print(f"active element 1st: {active_element}")
    if active_element.count() > 0:
        has_type = active_element.get_attribute("type") in ["date", "month"]
    if not has_type:
        active_element = page.evaluate_handle("document.activeElement")"""
        # has_type = page.evaluate("""() => ["date", "month"].includes(document.activeElement?.getAttribute("type"))""")
    """active_element = active_element.as_element()

    if has_type:
        print(f"active element: {active_element}")
        try:
            desired_date = datetime.strptime(desired_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            try:
                desired_date = datetime.strptime(desired_date, "%m/%Y").strftime("%Y-%m")
            except ValueError:
                desired_date = datetime.strptime(desired_date, "%Y").strftime("%Y")
        try:
            active_element.fill(desired_date)
        except Exception:
            print("active element filling didn't work")"""
    
    previous_attempt = False
    for attempt in range(4):
        state, image1, image2, page_x, page_y, previous_attempt, complete = calendar_time_process(current_answer=current_answer, desired_date=desired_date, image1=image1, image2=image2, full_page_width=full_page_width, page_x=page_x, page_y=page_y, current_attempt=attempt, previous_attempt=previous_attempt, state=state)
        if complete:
            break
    current_answer = ["white_pixel", -1]
    context = state.get("context")
    page_count = len(context.pages)
    state = execute_action(current_answer=current_answer, current_box=-1, full_page_width=full_page_width, full_page_height=600, page_count=page_count, state=state)
    return state

def find_time_process(current_question: str, desired_date: str, state: ApplicationState):
    page = state["current_page"]["page"]
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    page_elements = []
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        page_elements.append([icon, box_type, coordinates, coordinates, content])
    prompt = f"""
Your job is to the look at the current question, 1st determine if the current question is answered correctly with the Desired Date.

If current question is answered correctly stop and return {{action: None, complete: True}}

If the question is not answered correctly you will look at the current question and click the icon that is the calendar icon or the text space to fill out the question.

Current Question: {current_question}

Desired Date: {desired_date}

Only look at the current 

Look at the page elements and give us the icon that we can click to possibly open up the current question with it being sorted in order.

Look at Page Elements and the image to help find your icon.


PAGE ELEMENTS FORMAT
[icon, type, coordinates, content]

Page Elements: {page_elements}

Action
click - we will always choose click for our action, this clicks the icon.

Example output 1
{{
action: None
complete: True

The current question matches the desired date and we should return complete.
}}

Example output 2
{{
action: "click"
icon: 12
complete: False

The icon that I picked was the calendar icon.
}}

Example output 3
{{
action: "click"
icon: 48
complete: False

The icon that I picked was the box/text input for the current question.
}}
"""
    response = find_time_process_llm2.invoke([
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
    print(f"find time process answer: {answer}")
    action = answer.get("action")
    icon = answer.get("icon")
    complete = answer.get("complete")
    if complete:
        return state, 0, 0, complete
    current_answer = [action, icon]
    current_box = boxes_details[icon]
    bbox = current_box["bbox"]
    coordinates = [bbox[0], bbox[1], bbox[2], bbox[3]]
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    context = state.get("context")
    page_count = len(context.pages)
    page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    return state, page_x, page_y, complete

def review_find_time_process(current_question: str, full_page_width: int, page_x: int, page_y: int, state: ApplicationState):
    page = state["current_page"]["page"]
    pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 910))
    buffer = io.BytesIO()
    pyautogui_image.save(buffer, format="PNG")
    pyautogui_bytes = buffer.getvalue()
    encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    data = response.json()
    pyautogui_encoded_bytes = data["encoded_bytes"]
    boxes_details = data["boxes_details"]
    pyautogui_encoded_bytes = boxes_only_process(encoded_bytes=pyautogui_encoded_bytes, boxes_details=boxes_details)

    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)

    image2_elements = ""
    for i in range(len(boxes_details)):
        current_box = boxes_details[i]
        icon = current_box["icon"]
        box_type = current_box["type"]
        bbox = current_box["bbox"]
        coordinate = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
        content = current_box["content"]
        image2_elements += f"{icon}, {box_type}, {coordinate}, {content}\n"

    prompt = f"""
You are an AI Applicant Helper in the Review Find Time Process.

Here are your responsibilities:

1. See if image1 has a calendar popup.
2. See if image2 has a calendar popup.
3. If both images have no calendar popup, look at past attempts and your current page elements to determine what icon to click within image2.

If both image1 and image2 don't have any calendar popup, look at image2 and Image2 Elements to find the icon to click to open the calendar for the current question.

Current Question: {current_question}

Image2 Elements Format:
[icon, type, coordinates, content]

Image2 Elements: {image2_elements}

Action Explanation:
click - We will click the icon that you choose from image2.

Example Output 1:

{{
    "image1": True,
    "image2": False
}}

Image1 had a calendar popup but image2 did not.

Example Output 2:

{{
    "image1": False,
    "image2": True
}}

Image2 had a calendar popup but image1 did not.

Example Output 3:

{{
    "action": "click",
    "icon": 74,
    "image1": False,
    "image2": False
}}

Image1 and image2 did not have a calendar popup.

We click icon 74 within image2 of the current question because it was the calendar icon for the current question.

Always choose action click for action in this type of output.
"""
    response = review_find_time_process_llm2.invoke([
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
    answer = response["parsed"]
    print(f"review find time answer: {answer}")
    action = answer.get("answer")
    icon = answer.get("icon")
    image1 = answer.get("image1")
    image2 = answer.get("image2")
    if image1 or image2:
        return state, image1, image2, page_x, page_y
    current_answer = [action, icon]
    current_box = boxes_details[icon]
    bbox = current_box["bbox"]
    coordinates = [bbox[0], bbox[1], bbox[2], bbox[3]]
    full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
    context = state.get("context")
    page_count = len(context.pages)
    page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
    state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    return state, image1, image2, page_x, page_y


def text_time_process(current_question: str, full_page_width: int, state: ApplicationState):
    page = state["current_page"]["page"]
    pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 910))
    buffer = io.BytesIO()
    pyautogui_image.save(buffer, format="PNG")
    pyautogui_bytes = buffer.getvalue()
    encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
    data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
    response = requests.post("http://127.0.0.1:8000/image_process", json=data)
    data = response.json()
    pyautogui_encoded_bytes = data["encoded_bytes"]
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

You will only be looking at the current question this entire time and will ignore every other question.

Fill current question: {current_question} Time Process.
1. Find the Current Question we are on and only look at the current question.
2. Find what position we are highlighted in the current question.
3. Look at the highlighted text within the current question and determine how many moves left we need to be to be at the left-most position in the time text.
4. Answer the current question by using the USER PROFILE

Response Template
- action: This tells us what action we are going to use to fill this text
- left_arrow: This tells us how many arrows left we need to move to be at the left most postion
- text: This is the exact text we will enter to answer the current question by looking at the USER PROFILE. Always answer in numbers format

Example output 1

{{
    "action": "fill",
    "left_arrow": 2,
    "text": "08/21/2026"

We need to move two positions left to be at the left most position. I answered the current question with the user profile and entered the text in the format the current question wants us to give us in.

always answers text in numbers format.
}}

Example output 2

{{
    "action": "fill",
    "left_arrow": 0,
    "text": "09/2026"

We are currently at the left most position so we need to move 0 spots left. I answered the question exactly with the text that needed to be inputted in the format of the response guidance.

always answers text in numbers format.
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
    
    prompt = f"""
You're an AI Applicant Helper in the Text Time Process.

You have 4 responsibilities.

1. Answer the question.
2. Determine how many arrow keys we need to move to the left to be at the farthest left point on the current question. Look at what's highlighted within the current question.
3. Determine if image 1 has a calendar popup.
4. Determine if image 2 has a calendar popup.

Current Question: {current_question}

IMPORTANT

- Look at the current question to determine if we need to answer with the year, month & year, or day, month & year.
- Look at the User Profile to answer the question.
- Look at the images to determine how many arrow keys we need to move to the left to be at the farthest left point of the current question.
- Always choose the action of "fill".
- Always have the date be in numbers format.

Example 1

{{
    "action": "fill",
    "desired_date": "08/13/2026",
    "left_arrow": 1,
    "image1": True,
    "image2": False
}}

We answer the question with 08/13/2026 because they are looking for month, day, and year. We need to move one arrow to the left to be at the farthest point to the left to fill in the text. Image 1 has a calendar popup but Image 2 does not have a calendar popup.

Example 2

{{
    "action": "fill",
    "desired_date": "08/2028",
    "left_arrow": 0,
    "image1": False,
    "image2": True
}}

We answered the current question with month and year because that's all the current question is asking for. We are already at the farthest point to the left to answer the question. Image 1 does not have a calendar popup but image 2 does have a calendar popup.

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
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{pyautogui_encoded_bytes}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
            ]
        }
    ])
    details = response["raw"]
    new_tokens, model_name = details_process(details=details)
    state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)
    answer = response["parsed"]
    print(f"time text answers: {answer}")
    action = answer.get("action")
    desired_date = answer.get("desired_date")
    left_arrow = answer.get("left_arrow")
    image1 = answer.get("image1")
    image2 = answer.get("image2")
    if action:
        for i in range(left_arrow):
            pyautogui.hotkey("left")
        page.keyboard.type(desired_date)
    return state, desired_date, image1, image2

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

def month_calculator(current_month: int, current_year: int, desired_month: int, desired_year: int):
    return (desired_year - current_year) * 12 + (desired_month - current_month)

def calendar_time_process(current_answer: list, desired_date: str, image1: bool, image2: bool, full_page_width: int, page_x: int, page_y: int, current_attempt: int, previous_attempt: False, state: ApplicationState):
    page = state["current_page"]["page"]
    active_element = page.locator(":focus")
    print(f"calendar active element: {active_element}")
    active_element = page.evaluate_handle("document.activeElement")
    print(f"calendar document active element: {active_element}")
    
    encoded_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
    encoded_bytes = boxes_only_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details)
    image1_elements = ""
    image2_elements = ""
    if image2 or (not image1 and not image2):
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            bbox = current_box["bbox"]
            coordinate = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
            content = current_box["content"]
            image2_elements += f"{icon}, {box_type}, {str(coordinate)}, {content}\n"
    if image1 and not image2:
        print("used the page_x and page_y to click the calendar icon for image1")
        page.mouse.click(page_x, page_y)
        time.sleep(0.2)
    if not image2:
        pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 910))
        buffer = io.BytesIO()
        pyautogui_image.save(buffer, format="PNG")
        pyautogui_bytes = buffer.getvalue()
        encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
        data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
        response = requests.post("http://127.0.0.1:8000/image_process", json=data)
        data = response.json()
        pyautogui_encoded_bytes = data["encoded_bytes"]
        boxes_details = data["boxes_details"]
        pyautogui_encoded_bytes = boxes_only_process(encoded_bytes=pyautogui_encoded_bytes, boxes_details=boxes_details)
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            bbox = current_box["bbox"]
            coordinate = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
            content = current_box["content"]
            image1_elements += f"{icon}, {box_type}, {str(coordinate)}, {content}"
        
    prompt = f"""
You're an AI Applicant Helper in the Calendar Time Process.

Your job is to determine if the question is correct, find the calendar popup, and determine which icon to click. You will go through the Calendar Time Process to answer this question.

You will only be looking at the current question this entire time and will ignore every other question.

Current Question: {current_answer}

Desired Date: {desired_date}

Calendar Time Process

If the question is answered correctly stop and return, {{"action": None, complete: True}}

1. First find the question, if the question is answered correctly stop and return, {{"action": None, "complete": True}}
2. Next if the question is not correct and there is no calendar popup in the images stop and return, {{"action": None, "complete": False, reason: whatever your reason is and cite the images as your source.}}
3. Next determine what type of calendar it is between click_day, click_month, click_year.
4. If the calendar showcases the days that means we are in the click_day calendar.
5. Click_day, if we are in the desired month and year click the day icon of the desired day.
6. If we are not in the desired month and year click the arrows to move it to the desired month and year.
7. If the calendar showcases just the year and the months we are in the click_month calendar.
8. If we are in the correct year click the correct month for the calendar.
9. If we are not in the correct year for the calendar click the arrows to move it to the correct year.
10. If you only see the year in the calendar popup we are in the click_year calendar.
11. Click the year that matches the desired year or the closest to the desired year as possible.

Action Explanation
click_day: we choose click_day when we see days inside the calendar popup
click_month: we choose click_month when we see the year and the months but no days.
click_year: we choose click_year when we just see the year and no months or days.


Use the Page Elements and the images to find your icon.

PAGE ELEMENTS FORMAT

[icon, type, coordinates, content]

Image 1 page elements: {image1_elements}

Image 2 page elements: {image2_elements}

Example 1

{{
    "action": None,
    "complete": True
}}

The current question is answered correctly.

Example 2

{{
    "action": None,
    "complete": False
}}

The current question is answered incorrectly with no calendar popup in the images.

Example 3

{{
    "action": "click_day",
    "icon": 88,
    "current_day": 1,
    "desired_day": 20,
    "current_month": 8,
    "desired_month": 12,
    "current_year": 2004,
    "desired_year": 2028,
    "image2": True
    complete: False
}}

You must have action, icon, current_day, desired_day, current_month, desired_month, current_year, desired_year when doing the click_day.

We will click the arrow icon if the current month and current year don't match the desired month and year.

If the current month and year match the desired month and year we will click the day for the icon.

We are clicking the icon within page 2.

Example 4

{{
    "action": "click_month",
    "icon": 55,
    "current_month": 5,
    "desired_month": 3,
    "current_year": 2045,
    "desired_year": 2025,
    "image1": True
    complete: False
}}
You must have action, icon, current_month, desired_month, current_year, desired_year when doing the click_month.

If the current year and desired year match, click the desired month icon. If the current year and desired year don't match then click the arrow icon that will move us in the direction to the desired year.

We are clicking the icon within image 1 page elements.

Example 5

{{
    "action": "click_year",
    "icon": 28,
    "current_year": 2028,
    "desired_year": 2024,
    "image2": True
    complete: False
}}
You must have action, icon, current_year, desired_year when doing the click_year.

We will always click the icon that matches the desired year and if you don't see the desired year click the icon that is the closest to the desired year.

We are clicking the icon within image 2 page elements.

"""

    if image2:
        response = calendar_time_process_llm2.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}}
                ]
            }
        ])
    else:
        response = calendar_time_process_llm2.invoke([
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
    image1 = answer.get("image1")
    image2 = answer.get("image2")
    print(f"calendar time answer: {answer}")
    if complete:
        previous_attempt = False
        return state, image1, image2, page_x, page_y, previous_attempt, complete
    if not action and not complete:
        print("going to use find time and review time process")
        previous_attempt = True
        state, page_x, page_y, complete = find_time_process(current_question=current_answer, desired_date=desired_date, state=state)
        if complete:
            return state, image1, image2, page_x, page_y, previous_attempt, complete
        state, image1, image2, page_x, page_y = review_find_time_process(current_question=current_answer, full_page_width=full_page_width, page_x=page_x, page_y=page_y, state=state)
        if not image1 and not image2:
            state, image1, image2, page_x, page_y = review_find_time_process(current_question=current_answer, full_page_width=full_page_width, page_x=page_x, page_y=page_y, state=state)
        return state, image1, image2, page_x, page_y, previous_attempt, complete
    if action:
        state = calendar_action_process(action=action, icon=icon, current_day=current_day, current_month=current_month, current_year=current_year, desired_day=desired_day, desired_month=desired_month, desired_year=desired_year, boxes_details=boxes_details, image2=image2, full_page_width=full_page_width, current_attempt=current_attempt, previous_attempt=previous_attempt, state=state)
    previous_attempt = False
    return state, image1, image2, page_x, page_y, previous_attempt, complete

def calendar_action_process(boxes_details: list[dict], full_page_width: int, image2: bool, current_attempt: int, state: ApplicationState, action=None, icon=None, current_day=None, current_month=None, current_year=None, desired_day=None, desired_month=None, desired_year=None, previous_attempt=None):
    print(f"calendar attempt: {current_attempt}")
    print(f"image2 yes or no: {image2}")
    page = state["current_page"]["page"]
    context = state.get("context")
    page_count = len(context.pages)
    active_element = page.locator(":focus")
    has_type = False
    if active_element.count() > 0:
        has_type = active_element.get_attribute("type") in ["date", "month"]
    if not has_type:
        active_element = page.evaluate_handle("document.activeElement")
        try:
            has_type = page.evaluate("""() => ["date", "month"].includes(document.activeElement?.getAttribute("type"))""")
        except Exception:
            has_type = False
    if action != "white_pixel":
        current_box = boxes_details[icon]
        coordinates = current_box["bbox"]
        if image2:
            print("coordinates processed used for playwright")
            full_page_height = page.evaluate("""() => { return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight ); }""")
            page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=full_page_height)
        else:
            print("coordinates processed used for pyautogui")
            page_x, page_y = coordinates_process(coordinates=coordinates, full_page_width=full_page_width, full_page_height=870)
            page_x += 10
            page_y += 40
    if action == "click_day":
        if current_attempt == 0 or (previous_attempt and not image2) or has_type:
            days_apart = day_calculator(current_day=current_day, current_month=current_month, current_year=current_year,desired_day=desired_day, desired_month=desired_month, desired_year=desired_year)
            if days_apart > 0:
                for i in range(days_apart):
                    page.keyboard.press("ArrowRight")
            elif days_apart < 0:
                for i in range(abs(days_apart)):
                    page.keyboard.press("ArrowLeft")
        else:
            if current_month == desired_month and current_year == desired_year:
                if image2:
                    page.mouse.click(page_x, page_y)
                else:
                    print("using pyautogui to click a day")
                    pyautogui.click(page_x, page_y)
            else:
                months_apart = month_calculator(current_month=current_month, current_year=current_year, desired_month=desired_month, desired_year=desired_year)
                if image2:
                    for i in range(abs(months_apart)):
                        page.mouse.click(page_x, page_y)
                else:
                    for i in range(abs(months_apart)):
                        pyautogui.click(page_x, page_y)
    elif action == "click_month":
        years_apart = desired_year - current_year
        if current_attempt == 0 or (previous_attempt and not image2) or has_type:
            total_months = month_calculator(current_month=current_month, current_year=current_year, desired_month=desired_month, desired_year=desired_year)
            if total_months > 0:
                for i in range(total_months):
                    pyautogui.hotkey("right")
            else:
                for i in range(abs(total_months)):
                    pyautogui.hotkey("left")
        elif years_apart != 0:
            if image2:
                for i in range(abs(years_apart)):
                    page.mouse.click(page_x, page_y)
            else:
                for i in range(abs(years_apart)):
                    pyautogui.click(page_x, page_y)
        else:
            print("clicking month")
            if image2:
                print("used playwright for click")
                page.mouse.click(page_x, page_y)
            else:
                print("used pyautogui for click")
                pyautogui.click(page_x, page_y)
    elif action == "click_year":
        total_click = abs(desired_year - current_year)
        if current_attempt == 0 or (previous_attempt and not image2):
            if image2:
                for i in range(total_click):
                    page.keyboard.press("ArrowRight")
            else:
                for i in range(total_click):
                    pyautogui.click(page_x, page_y)
        else:
            if image2:
                page.mouse.click(page_x, page_y)
            else:
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
    white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details, full_page_width=full_page_width, full_page_height=full_page_height)
    if white_x and white_y:
        page.mouse.click(white_x, white_y)
        time.sleep(2)
    return state

def markdown_process(current_answer: list, ai_answers: list[list], markdown_type: str, image1: bool, image2: bool, state: ApplicationState, white_x=None, white_y=None):
    # state = time_process(current_answer=current_answer, desired_date=desired_date, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, cut_off_height=cut_off_height, page_x=page_x, page_y=page_y, state=state)
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

def dropdown_process(current_answer: list, previous_action: str, old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, page_x: int, page_y: int, first_text: str, desired_text: str, desired_option: str, total_options: int, image1: bool, image2: bool, state: ApplicationState):
    print("we are at dropdown process")
    print(f"current answer: {current_answer}")
    page = state["current_page"]["page"]
    context = state.get("context")
    page_count = len(context.pages)
    arrow_temp_status = True
    arrow_permanent_status = False
    needs_scroll = False
    previous_answers = []
    for i in range(6):
        body_text = page.locator("body").inner_text() or None
        encoded_bytes, full_page_width1, full_page_height1 = screenshot_process(state=state)
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        if full_page_height == old_page_height:
            print("used pixel image cropping in dropdown")
            encoded_bytes, min_cut_off_height, max_cut_off_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=encoded_bytes)
        else:
            print("used cropped image process in dropdown")
            encoded_bytes, min_cut_off_height, max_cut_off_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=encoded_bytes, boxes_details2=boxes_details, cut_off_height=cut_off_height, full_page_width=full_page_width, old_page_height=old_page_height, state=state)
        
        if min_cut_off_height is None or max_cut_off_height is None:
            print("min cut off height is None")
            min_cut_off_height = 0
            max_cut_off_height = 0

        encoded_bytes, boxes_details, do_not_use, do_not_use2 = omniparser_process(encoded_bytes=encoded_bytes, state=state)
        decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
        buffer1 = io.BytesIO(decoded_bytes)
        image1 = Image.open(buffer1)
        # image1.show()
        full_page_width2, full_page_height2 = image1.size
        if not image1:
            pyautogui_image = pyautogui.screenshot(region=(10, 40, full_page_width, 910))
            buffer = io.BytesIO()
            pyautogui_image.save(buffer, format="PNG")
            pyautogui_bytes = buffer.getvalue()
            pyautogui_encoded_bytes = base64.b64encode(pyautogui_bytes).decode("utf-8")
            data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
            response = requests.post("http://127.0.0.1:8000/image_process", json=data)
            data = response.json()
            pyautogui_encoded_bytes = data["encoded_bytes"]
            pyautogui_boxes_details = data["boxes_details"]
            pyautogui_encoded_bytes = boxes_only_process(encoded_bytes=pyautogui_encoded_bytes, boxes_details=pyautogui_boxes_details)
        page_elements = []
        for i in range(len(boxes_details)):
            current_box = boxes_details[i]
            icon = current_box["icon"]
            box_type = current_box["type"]
            bbox = current_box["bbox"]
            coordinates = [round(bbox[0], 4), round(bbox[1], 4), round(bbox[2], 4), round(bbox[3], 4)]
            content = current_box["content"]
            page_elements.append([icon, box_type, coordinates, content])
        print(f"desired answer: {desired_text}")
        if arrow_permanent_status:
            print("going down where arrow does work")
            prompt = f"""
    You're an AI Applicant Helper in the Dropdown Process.

    You will only be looking at the current question.
    You will have to determine what type of action we will use and then answer the extra details that come with that action.
    You will also have your previous answers to the dropdown question to help you understand the context.

    You will Follow the Dropdown Process to answer the current question.

    Current Question: {current_answer}

    previous answers: {previous_answers}

    Body Text: {body_text}

    Page Elements Format:
    [icon, type, coordinates, content]

    Page Elements: {page_elements}

    Dropdown Process:
    1. First find the current question in the photo.
    2. If the current question's answer is the desired answer based on the User Profile, stop and follow this subprocess.

    - If there are other questions on the screen or there is no exit icon stop and return something like this.
    - Ex: {{action: “white_pixel”, icon: -1, complete: True}}
    - If there is some type of exit icon that is needed to click to leave the current question then return something like this.
    - Ex: {{action: “click”, icon: 8, complete: True}}

    2. If there are options on the screen follow this subprocess.
    - If the desired option is on the screen then click it. Return something like this.
    - Ex: {{action: click, icon: 12, reason: whatever your reason is (your reason helps future answers)}}
    - If the desired option is not seen then follow this return process. 
    - Find the current option in the photo and the desired_option, the total amount of options, first option text that appears in the photo, desired text. Return something like this.
    - Ex: {{action: arrow, current_option: 8, desired_option: 4, total_options: 80, reason: whatever your reason is (your reason helps future answers)}}
    - If there is text that needs to be inputted for the current question, find the icon that needs to be clicked and look at the User Profile to answer the Current Question.
    - return something like this (just because there is a place to input text for the current question doesn't mean we need to input text, think logically to determine if we do or don't need to).
    - You also need to determine if this requires a basic fill in or is this something we need to search for.
    - If this is just a basic fill in text box then return something like this.
    - Ex: {{action: fill, icon: 6, action_text: no, reason: whatever your reason is (your reason helps future answers)}}
    - If this is a text box where we need to search for the answer then return something like this.
    - Ex: {{action: search, icon: 8, list_text: [skill 1, skill 2], reason: whatever your reason is (your reason helps future answers)}}
    - Ex: {{action: search, icon: 12, list_text: [skill 4], reason: whatever your reason is (your reason helps future answers)}}

    3. If there is no options present follow this route
    - Find the icon that is going to reopen the current question that will allow us to continue the drop down process.
    - Ex: {{action: click, icon: 20}}

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
        elif arrow_temp_status and not arrow_permanent_status:
            print("going down arrow temp status and not arrow permanent status")
            print(f"previous action: {previous_action}")
            prompt = f"""
    You're an AI Applicant Helper in the Dropdown Process.

    You will only be looking at the current question.
    You will have to determine what type of action we will use and then answer the extra details that come with that action.
    You will also have your previous answers to the dropdown question to help you understand the context.

    You will Follow the Dropdown Process to answer the current question.

    Current Question: {current_answer}

    Previous Action: {previous_action}

    previous answers: {previous_answers}

    Body Text: {body_text}

    Page Elements Format:
    [icon, type, coordinates, content]

    Page Elements: {page_elements}

    Dropdown Process:
    1. First find the current question in the photo.
    2. If the current question's answer is the desired answer based on the User Profile, stop and follow this subprocess.    - If there are other questions on the screen or there is no exit icon stop and return something like this.
    - Ex: {{action: “white_pixel”, icon: -1, complete: True, reason: whatever your reason}}
    - If there is some type of exit icon that is needed to click to leave the current question then return something like this.
    - Ex: {{action: “click”, icon: 8, complete: True, reason: whatever your reason}}

    2. If the previous action was arrow follow this subprocess.
    - If there are no options on the screen or we chose the first option in {first_text}. Find the icon to click that reopens the current question and return something like this.
    - Choose this option if we clicked {first_text} or there are no options on the screen.
    - If there are options still shown on the screen and you see the first option: {first_text} in the image that means we need to use the scroll process.
    - Ex: {{action: "click", icon: 28, arrow_status: False, reason: : Looking at the current question, we chose the first text and the icon is closed that needs to reopened.(your reason helps future answers)}}
    - If there are options still shown on the screen and you see the first option: {first_text} in the image that means we need to use the scroll process.
    - Scroll process needs you to find the current_option (usually the option that is highlighted in the image if not just choose the first option that is shown in the image for the current question), desired_option, total_options, and desired_text, if move down is True that means we are moving downwards to find our option, if move down is False we are moving up to Find our option, return something like this.
    - Ex: {{action: scroll, current_option: 2, desired_option: 8, total_options: 20, current_text: option 2, desired_text: option 8, arrow_status: False, move_down: True, reason: The question is not answered and there is no options for the current question on the screen and the correct option is downwards. (your reason helps future answers)}}
    - Your reasoning for choosing scroll should only be if the first text is shown or there is no options listed with no answer. That means if there is an answer to the question do not choose scroll.

    3. You need to look at the current question, image, body text, and page elements, and the USER PROFILE to correctly answer the question.
    - If the desired option is on the screen then click it and return something like this.
    - Ex: {{action: click, icon: 12, reason: whatever your reason is (your reason helps future answers)}}
    - If you cannot find the icon for desired option then find the current option which is usually highlighted in the image, if not just go with the first option shown, find the desired option, first_text (first option text), and the desired text to answer the question.
    - {{action: arrow, current_option: 0, desired_option: 4, reason: whatever your reason is (your reason helps future answers)}}
    - If there is text that needs to be inputted to answer the current question (just because there is a text input spot doesn't automatically mean that text needs to be inputted, think logically to determine if text needs to be inputted to answer the question), find the icon that needs to be clicked and look at the User Profile to answer the Current Question.
    - If this is just a basic fill in text box then return something like this.
    - Ex: {{action: fill, icon: 6, action_text: no, reason: whatever your reason is (your reason helps future answers)}}
    - If this is a text box where we need to search for the answer then return something like this.
    - Ex: {{action: search, icon: 8, list_text: [skill 1, skill 2], reason: whatever your reason is (your reason helps future answers)}}
    - Ex: {{action: search, icon: 12, list_text: [skill 4], reason: whatever your reason is (your reason helps future answers)}}

    3. If there is no options present follow this route
    - If there is no options/input text that is for the current question that means we need to click the icon of the current question to reopen the question.
    - Find the icon by looking at the page elements and the image to reopen the question.
    - Ex: {{action: click, icon: 28}}

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
        else:
            print("going down the process where arrow doesn't work and we must use scroll")
            prompt = f"""
    You're an AI Applicant Helper in the Dropdown Process.

    You will only be looking at the current question.
    You will have to determine what type of action we will use and then answer the extra details that come with that action.
    You will also have your previous answers to the dropdown question to help you understand the context.

    You will Follow the Dropdown Process to answer the current question.

    Current Question: {current_answer}

    previous answers: {previous_answers}
    
    Body Text: {body_text}

    Page Elements Format:
    [icon, type, coordinates, content]

    Page Elements: {page_elements}

    Dropdown Process:
    1. First find the current question in the photo.
    2. If the current question's answer is the desired answer based on the User Profile, stop and follow this subprocess.    - If there are other questions on the screen or there is no exit icon stop and return something like this.
    - If there are other questions on the screen or there is no exit icon stop and return something like this.
    - Ex: {{action: “white_pixel”, icon: -1, complete: True}}
    - If there is some type of exit icon that is needed to click to leave the current question then return something like this.
    - Ex: {{action: “click”, icon: 8, complete: True}}

    2. You need to look at the current question, image, body text, and page elements, and the USER PROFILE to correctly answer the question.
    - If the desired option is on the screen then click it and return something like this.
    - Ex: {{action: click, icon: 12, reason: whatever your reason is (your reason helps future answers)}}
    - Scroll process needs you to find the current_option (usually the option that is highlighted in the image if not just choose the first option that is shown in the image for the current question), desired_option, total_options, and desired_text, if move down is True that means we are moving downwards to find our option, if move down is False we are moving up to Find our option, return something like this.
    - Ex: {{action: scroll, current_option: 10, desired_option: 5, total_options: 20, current_text: option 2, desired_text: option 8, move_down: False, reason: we need to move upward to find our desired option. (your reason helps future answers).}}
    - If there is text that needs to be inputted to answer the current question (just because there is a text input spot doesn't automatically mean that text needs to be inputted, think logically to determine if text needs to be inputted to answer the question), find the icon that needs to be clicked and look at the User Profile to answer the Current Question.
    - If this is just a basic fill in text box then return something like this.
    - Ex: {{action: fill, icon: 6, action_text: no, reason: whatever your reason is (your reason helps future answers)}}
    - If this is a text box where we need to search for the answer then return something like this.
    - Ex: {{action: search, icon: 8, list_text: [skill 1, skill 2], reason: whatever your reason is (your reason helps future answers)}}
    - Ex: {{action: search, icon: 12, list_text: [skill 4], reason: whatever your reason is (your reason helps future answers)}}

    3. If there is no options present follow this route
    - If there is text that needs to be inputted for the current question, find the icon that needs to be clicked and look at the User Profile to answer the Current Question and return something like this.
    - Ex: {{action: fill, icon: 6, action_text: yes, reason: whatever your reason is (your reason helps future answers)}}
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
        
        if not image1:
            response = dropdown_process_llm2.invoke([
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{pyautogui_encoded_bytes}"}}
                    ]
                }
            ])

        else:
            response = dropdown_process_llm2.invoke([
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
        previous_answers.append(answer)
        print(f"dropdown answer: {answer}")
        action = answer.get("action")
        icon = answer.get("icon")
        complete = answer.get("complete")
        arrow_status = answer.get("arrow_status")
        current_option = answer.get("current_option")
        desired_option = answer.get("desired_option")
        total_options = answer.get("total_options")
        current_text = answer.get("current_text")
        desired_text = answer.get("desired_text")

        action_text = answer.get("action_text")
        list_text = answer.get("list_text")
        move_down = answer.get("move_down")
        if arrow_temp_status == True and previous_action == "arrow":
            print("seeing if setting arrow status permanently works")
            print(f"arrow status: {arrow_status}")
            if arrow_status == True:
                arrow_permanent_status = True
                arrow_temp_status = False
            elif arrow_status == False or action == "scroll":
                arrow_permanent_status = False
                arrow_temp_status = False
        previous_action = action
        if complete:
            if action == "click":
                if icon is not None and icon <= len(boxes_details):
                    current_answer = [action, icon]
                    current_box = boxes_details[icon]
                    desired_bbox = cropped_coordinates_process(full_page_height1=full_page_height1, full_page_height2=full_page_height2, min_cut_off_height=min_cut_off_height, desired_bbox=current_box["bbox"])
                    current_box["bbox"] = desired_bbox
                    state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
            else:
                state = execute_action(current_answer=["white_pixel", -1], current_box=-1, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
            return state
        elif action == "click":
            new_answer = [action, icon]
            if icon is not None and icon <= len(boxes_details):
                current_box = boxes_details[icon]
                desired_bbox = cropped_coordinates_process(full_page_height1=full_page_height1, full_page_height2=full_page_height2, min_cut_off_height=min_cut_off_height, desired_bbox=current_box["bbox"])

                current_box["bbox"] = desired_bbox
                state = execute_action(current_answer=new_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
        elif action == "arrow":
            new_answer = [action, current_option, desired_option]
            state = execute_action(current_answer=new_answer, current_box=-1, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
        elif action == "fill":
            if icon is not None and icon <= len(boxes_details):
                new_answer = [action, icon, action_text]
                current_box = boxes_details[icon]
                desired_bbox = cropped_coordinates_process(full_page_height1=full_page_height1, full_page_height2=full_page_height2, min_cut_off_height=min_cut_off_height, desired_bbox=current_box["bbox"])
                current_box["bbox"] = desired_bbox
                state = execute_action(current_answer=new_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
        elif action == "scroll":
            state = scroll_process(current_answer=current_answer, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_x=page_x, old_y=page_y, old_page_width=full_page_width, old_page_height=old_page_height, cut_off_height=cut_off_height, desired_option=desired_option, total_options=total_options, first_text=current_text, desired_text=desired_text, move_down=move_down, state=state)
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
1. First determine if the question is finished and answered correctly. If it is return this.
- Ex: {{action: white_pixel, icon: -1, complete: True}}
2. First determine if the options for the current question is open or not
3. If you see no options that means we need to reopen the box again.
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
    if action == "arrow":
        state = execute_action(current_answer=current_answer, current_box=-1, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
        return state
    icon = current_answer[1]
    current_box = boxes_details[icon]
    state = execute_action(current_answer=current_answer, current_box=current_box, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)
    return state

def search_process( current_answer: str, list_text: list[str], state: ApplicationState, process=None):
    page = state["current_page"]["page"]
    context = state.get("context")
    page_count = len(context.pages)
    complete = False
    current_text = list_text[0]
    print(f"answers: {list_text}")
    for attempt in range(4):
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
        body_text = page.locator("body").inner_text()
        prompt = f"""
Your an AI applicant helper whose job is to help us out in the search process.
We have just entered some text and your job is to tell us one of a few things. 
Only look at the current question and ignore the rest, our job is to only answer the current question.
current_question: {current_answer}
Body Text: {body_text}

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
all_options: [Alabama, Arkansas, california, mississippi, south carolina, north carlolina]
}}

Example 2
{{
action: "arrow"
current_option: 0
option_choice: 6
all_options: [Alabama, Arkansas, california, mississippi, south carolina, north carlolina]
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

def check_arrow_option(old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, cut_off_height: int, desired_text: str, state: ApplicationState):
    page = state["current_page"]["page"]

    comparison_bytes, full_page_width, full_page_height = screenshot_process(state=state)

    full_page_height = page.evaluate("""() => { return Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.offsetHeight,
        document.body.clientHeight,
        document.documentElement.clientHeight
    ); }""")

    if old_page_height == full_page_height:
        encoded_bytes, min_cut_off_height, max_cut_off_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=comparison_bytes)

    else:
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)

        encoded_bytes, min_cut_off_height, max_cut_off_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=comparison_bytes, boxes_details2=boxes_details, cut_off_height=cut_off_height, old_page_height=old_page_height, full_page_width=full_page_width, state=state)

    encoded_bytes, boxes_details, do_not_use, do_not_use2 = omniparser_process(encoded_bytes=encoded_bytes, state=state)

    desired_text = normalize_text(desired_text)

    for current_box in boxes_details:
        content = normalize_text(current_box.get("content", ""))

        print(f"Current box content: {content}")

        if not content:
            continue

        if content == desired_text:
            print(f"Found desired text: {content}")
            return True, state

    print(f"Desired text not found: {desired_text}")
    return False, state

def search_process(current_answer: list[str], list_text: list[str], old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, old_x: int, old_y: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    used_enter, state = check_search_options(old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, state=state)
    for i in range(len(list_text)+3):
        print("hello")


def search_process(current_answer: list[str], list_text: list[str], old_encoded_bytes: str, old_boxes_details: list[dict], old_page_height: int, old_x: int, old_y: int, cut_off_height: int, state: ApplicationState):
    page = state["current_page"]["page"]
    print(f"page: {page}")
    print(f"current answer: {current_answer}")
    context = state.get("context")

    typing_text = []
    if len(list_text) > 1:
        typing_text = list_text[1:]

    if len(list_text) <= 0:
        return state
    most_recent_search = list_text[0]
    previous_search = True
    previous_answers = []
    previous_action = None

    arrow_permanent_status = False
    arrow_checked = False

    need_to_leave = False

    for i in range(500):
        page.keyboard.press("ArrowRight")
    for i in range(500):
        page.keyboard.press("Backspace")

    page.keyboard.type(list_text[0])

    encoded_bytes, full_page_width, full_page_height = screenshot_process(state=state)

    if full_page_height == old_page_height:
        cropped_encoded_bytes, min_cut_off_height, max_cut_off_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=encoded_bytes)
    else:
        do_not_use, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)
        cropped_encoded_bytes, min_cut_off_height, max_cut_off_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=encoded_bytes, boxes_details2=boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, full_page_width=full_page_width, state=state)

    do_not_use, cropped_boxes_details1, do_not_use_width, do_not_use_height = omniparser_process(encoded_bytes=cropped_encoded_bytes, state=state)

    used_enter, state = check_search_options(old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, cropped_encoded_bytes=cropped_encoded_bytes, cropped_boxes_details1=cropped_boxes_details1, list_text=list_text, state=state)
    print(f"used enter: {used_enter}")

    for i in range(500):
        page.keyboard.press("ArrowRight")
    for i in range(500):
        page.keyboard.press("Backspace")

    page.keyboard.type(list_text[0])

    max_iterations = (len(list_text) * 2) - 1

    for iteration in range(max_iterations):

        print(f"Search iteration: {iteration + 1}/{max_iterations}")
        print(f"Desired text: {most_recent_search}")
        print(f"Previous search: {previous_search}")
        print(f"Used enter: {used_enter}")
        print(f"Arrow permanent status: {arrow_permanent_status}")

        print(f"page2: {page}")
        body_text = page.locator("body").inner_text() or ""

        encoded_bytes, full_page_width1, full_page_height1 = screenshot_process(state=state)
        do_not_use_bytes, boxes_details, full_page_width, full_page_height = omniparser_process(state=state)

        if previous_search == True:
            if full_page_height == old_page_height:
                encoded_bytes, min_cut_off_height, max_cut_off_height = pixel_image_cropping(encoded_bytes1=old_encoded_bytes, encoded_bytes2=encoded_bytes)
            else:
                encoded_bytes, min_cut_off_height, max_cut_off_height = cropped_image_process(encoded_bytes1=old_encoded_bytes, boxes_details1=old_boxes_details, encoded_bytes2=encoded_bytes, boxes_details2=boxes_details, cut_off_height=cut_off_height, full_page_width=full_page_width, old_page_height=old_page_height, state=state)
            encoded_bytes, boxes_details, do_not_use, do_not_use2 = omniparser_process(encoded_bytes=encoded_bytes, state=state)
        else:
            encoded_bytes = do_not_use_bytes

        if min_cut_off_height is None or max_cut_off_height is None:
            min_cut_off_height = 0
            max_cut_off_height = 0


        decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
        image1 = Image.open(io.BytesIO(decoded_bytes))
        image1.show()
        full_page_width2, full_page_height2 = image1.size

        page_elements = []

        for current_box in boxes_details:
            icon = current_box["icon"]
            box_type = current_box["type"]
            bbox = current_box["bbox"]
            coordinates = [round(value, 4) for value in bbox]
            content = current_box["content"]

            page_elements.append([icon, box_type, coordinates, content])
        print(f"page elements: {page_elements}")
        if not arrow_checked or arrow_permanent_status:
            print("Using arrow prompt")

            prompt = f"""
You're an AI Applicant Helper in the Search Process.

Your job is to answer the current question by searching for and selecting multiple items.

Current Question: {current_answer}

Desired Text: {most_recent_search}

Previous Search: {previous_search}

Body Text: {body_text}

Page Elements Format:
[icon, type, coordinates, content]

Page Elements: {page_elements}

Action type:
Click - this is used when we need to click a page element
arrow - this is used when we need to use the arrows to to find a option/dropdown option that is not visible.

SEARCH PROCESS:
1. Only focus on the current question.
2. Use the screenshot, Body Text, Page Elements, and Previous Search to come up with your answer.
3. We are currently trying to search for or click/arrow/scroll: {most_recent_search}.

If Previous search is False follow this subprocess:
1. We need to find the icon that will allow us to input the next text.
2. Find the current question and the icon that will allow us to input the next text and return something like this.
- {{action: click, icon: 12, typed_search: True, reason: We are clicking the icon that will allow us to enter the next text.}}

If Previous Search IS True follow this subprocess:
1. If there are no options/dropdown options available that means we need to find the icon to click that will allow us to enter our next text.
- Find the the search input for the current question and return something like this.
- Now click the desired text search and not any of the option/dropdown options.
{{"action": "click", "icon": 8, typed_search: True, "reason": "Opening the search input because there was no dropdown options available."}}
2. If the desired option: {most_recent_search} is not an option/something super similar then we will still cllick the search input icon and return something like this.
{{"action": "click", "icon": 8, typed_search: True, "reason": "Opening the search input because none of the options/dropdown options fit my desired option."}}

3. If there are options/dropdown available then follow this subprocess
- If the desired option: {most_recent_search} is visible then click it and return something like this.
- Only click the icon that is an option/dropdown option and not the text we searched for.
- {{"action": "click", "icon": 12, typed_search: False, "reason": "The desired option is visible, so we can click it directly."}}
- If the desired option: {most_recent_search} is not visible then follow this subproceess.
- Identify the current option, usually the highlighted option.
- If no option is highlighted, use the first visible option.
- Determine the current option position.
- Determine the desired option position.
- Return an arrow action like this.
{{"action": "arrow", "current_option": 2, "desired_option": 8, typed_search: False, "reason": "The desired option is not visible and is further down."}}

"""

        else:
            print("Using scroll prompt")

            prompt = f"""
You're an AI Applicant Helper in the Search Process.

Your job is to answer the current question by searching for and selecting multiple items.

Current Question: {current_answer}

Current Desired Text: {most_recent_search}

Previous Search: {previous_search}

Body Text: {body_text}

Page Elements Format:
[icon, type, coordinates, content]

Page Elements: {page_elements}

Action type:
Click - this is used when we need to click a page element
scroll - this is used when we need to choose the option/dropdown option that is not visible.

SEARCH PROCESS:
1. Only focus on the current question.
2. Use the screenshot, Body Text, Page Elements, and Previous Search to come up with your answer.
3. We are currently trying to search for or click/arrow/scroll: {most_recent_search}.

If Previous search is False follow this subprocess:
1. We need to find the icon that will allow us to input the next text.
2. Find the current question and the icon that will allow us to input the next text and return something like this.
- {{action: click, icon: 12, typed_search: True, reason: We are clicking the icon that will allow us to enter the next text.}}

If Previous Search IS True follow this subprocess:
1. If there are no options/dropdown options available that means we need to find the icon to click that will allow us to enter our next text.
- Find the the search input for the current question and return something like this.
- Now click the desired text search and not any of the option/dropdown options.
{{"action": "click", "icon": 8, typed_search: True, "reason": "Opening the search input because there was no dropdown options available."}}
2. If the desired option: {most_recent_search} is not an option/something super similar then we will still cllick the search input icon and return something like this.
{{"action": "click", "icon": 8, typed_search: True, "reason": "Opening the search input because none of the options/dropdown options fit my desired option."}}

3. If there are options/dropdown available then follow this subprocess
- If the desired option: {most_recent_search} is visible then click it and return something like this.
- Only click the icon that is an option/dropdown option and not the text we searched for.
- {{"action": "click", "icon": 12, typed_search: False, "reason": "The desired option is visible, so we can click it directly."}}
- If the desired option: {most_recent_search} is not visible then follow this subproceess.

- If the desired option: {most_recent_search} is not visible, but it may exist further up or down in the dropdown, follow this subprocess:
- Identify the current option, usually the highlighted option.
- If no option is highlighted, use the first visible option.
- Determine the current option position.
- Determine the desired option position.
- Estimate the total number of dropdown options.
- Determine whether we need to scroll upward or downward.
- If move_down is True, we need to scroll downward.
- If move_down is False, we need to scroll upward.
- Return a scroll action like this:

{{"action": "scroll", "current_option": 2, "desired_option": 8, "total_options": 50, "current_text": "Option 2", "desired_text": "{most_recent_search}", "move_down": True, "used_search": False, "reason": "The desired option is not visible and is further down."}}

- If the desired option is above the current option, return something like this:

{{"action": "scroll", "current_option": 10, "desired_option": 4, "total_options": 50, "current_text": "Option 10", "desired_text": "{most_recent_search}", "move_down": False, "used_search": False, "reason": "The desired option is not visible and is above."}}

IMPORTANT:

- Always prioritize clicking the desired option if it is visible.
- Only use scroll when the desired option is not visible but may exist further up or down.
- If no dropdown options exist, click the search input.
- If none of the available options are relevant to the desired option and further scrolling is not warranted, click the search input.
- Never use arrow navigation.
- Never select an unrelated option.
- Return exactly one action.
"""


        response = search_process_llm2.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_bytes}"}},
                ]
            }
        ])

        details = response["raw"]
        new_tokens, model_name = details_process(details=details)
        state = ai_token_tracker(new_tokens=new_tokens, model_name=model_name, state=state)

        answer = response["parsed"]
        previous_answers.append(answer)

        print(f"Search answer: {answer}")


        action = answer.get("action")
        icon = answer.get("icon")
        current_option = answer.get("current_option")
        desired_option = answer.get("desired_option")
        total_options = answer.get("total_options")
        current_text = answer.get("current_text")
        move_down = answer.get("move_down")
        typed_search = answer.get("typed_search")

        previous_action = action


        page_count = len(context.pages)
        if action == "click":
            print("do click")

            if icon is None:
                print("No icon provided for click.")
                continue

            current_box = boxes_details[icon]

            if previous_search == True:
                desired_bbox = cropped_coordinates_process(full_page_height1=full_page_height1, full_page_height2=full_page_height2, min_cut_off_height=min_cut_off_height, desired_bbox=current_box["bbox"])
                current_box["bbox"] = desired_bbox

            if typed_search == False:
                new_answer = ["click", icon]
                print("did not type")
            else:
                if len(typing_text) > 0:
                    print(f"did type this: {typing_text[0]}")
                    new_answer = ["fill", icon, typing_text[0]]
                    most_recent_search = typing_text[0]
            if typed_search != False and len(typing_text) <= 0:
                print("won't fill due to nothing to fill inside of typing text")
            else:
                if typed_search == True:
                    typing_text.pop(0)
                state = execute_action(current_answer=new_answer, current_box=current_box, full_page_height=full_page_height, full_page_width=full_page_width, page_count=page_count, state=state)

        elif action == "arrow":
            print("do arrow")

            if arrow_checked and not arrow_permanent_status:
                print("Arrow navigation is disabled.")
                continue

            new_answer = ["arrow", current_option, desired_option]

            state = execute_action(current_answer=new_answer, current_box=-1, full_page_width=full_page_width, full_page_height=full_page_height, page_count=page_count, state=state)

            if not arrow_checked:
                print("Checking arrow navigation for the first time")

                arrow_status, state = check_arrow_option(old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_page_height=old_page_height, cut_off_height=cut_off_height, desired_text=desired_text, state=state)

                arrow_checked = True
                arrow_permanent_status = arrow_status

                print(f"Arrow navigation works: {arrow_permanent_status}")

        elif action == "scroll":
            print("do scroll")

            state = scroll_process(current_answer=current_answer, old_encoded_bytes=old_encoded_bytes, old_boxes_details=old_boxes_details, old_x=old_x, old_y=old_y, old_page_width=full_page_width, old_page_height=old_page_height, cut_off_height=cut_off_height, desired_option=desired_option, total_options=total_options, first_text=current_text, desired_text=desired_text, move_down=move_down, state=state)

        previous_search = typed_search
        if len(typing_text) == 0 and (need_to_leave or iteration == 0):
            break
        else:
            need_to_leave = True


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

def exit_question_process(current_answer: str, ai_answers: list[list], state: ApplicationState, all_text=None, process=None):
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
    print(f"current question: {current_answer}")
    print(f"all text: {all_text}")
    print(f"page elements: {page_elements}")
    prompt = f"""
You are an AI Applicant Helper handling ONLY the current question.

Current Question: {current_answer}
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


        white_x, white_y = empty_pixel_process(encoded_bytes=encoded_bytes, boxes_details=boxes_details, full_page_width=full_page_width, full_page_height=full_page_height)

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
time: Any question that has anything to due with time. Requires icon + current_question.
delete: Clear incorrect/unwanted text. Requires icon.
click: Select/unselect an immediately answerable option. Requires icon.
search: When you need to search something or enter skills that could possibly add suggested drop downs, search texts must always be one word.
upload_resume: Resume upload field. Requires icon.
upload_cover_letter: Cover-letter upload field. Requires icon.
markdown: Dropdown/combobox/menu requiring option discovery and selection. Requires icon + current_question.
add_more: add another option will add more items for examples like add more education, add more experience, things of that nature


Page Elements format
[icon, type, coordinates, content]

PAGE ELEMENTS
{page_elements}

Actions Format
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

add_more: [action, icon, submit_text]


Example:

items: [["skip"], ["fill", 28, {state["email"]}], ["time", 35, "When do you graduate?"], ["delete", 38], ["delete_and_fill", 42, {state["first_name"]}], ["click", 32], ["search", ["python", "playwright", "java"]], ["search", 8, "What skills do you have", ["skill 1", "skill 2", "skill 3"]], ["upload_resume", 50], ["upload_cover_letter", 52], ["click_and_view", 22, "Add More Work Experience"], ["markdown", 60, "What U.S. State are you in?"], ["add_more", 30]]

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
    state["city"] = "Youngsville"
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
    state["work_experience"] = [{"company": "google", "position": "software engineer intern", "start_date": "May 2026", "end_date": "August 2026"}]
    state["education"] = [{"school": "UNC Charlotte", "major": "computer science", "start_date": "August 2025", "end_date": "May 2029"}, {"school": "UNC", "major": "mechanical engineer", "start_date": "August 2029", "end_date": "May 2033"}]


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
graph.add_conditional_edges("decide_page", decide_routing, {"cookies": "cookies_process", "apply": "apply_process", "signup": "signup_process", "forms": "signup_process", "wait": "wait_process", "complete": END, "exit": END})
graph.add_edge("cookies_process", "decide_page")
graph.add_edge("apply_process", "decide_page")
graph.add_conditional_edges("signup_process", signup_routing, {"max_tries": END, "total_cost": END, "complete": END, "new_form": "signup_process", "different_page": "decide_page", "decide_page": "decide_page"})
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
        final_state = mapping.invoke({"url": url2, "current_page": current_page, "token_usage": token_usage, "browser": browser, "context": context, "user_id": user_id, "wait_tracker": 0})
        print(f"final_state: {final_state}")
        leaving_reason = final_state.get("leaving_reason")
        print(f"Browser closing due to : {leaving_reason}")
        browser.close()


complete_application(url)
from rapidocr import RapidOCR

# Initialize the engine (defaults to ONNX Runtime)
engine = RapidOCR()
import numpy as np
from PIL import Image

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import numpy as np
from PIL import Image, ImageDraw

def test_rapidocr(image_path):
    image = Image.open(image_path).convert("RGB")
    image_array = np.asarray(image)
    image_width, image_height = image.size

    result = engine(image_array)

    if result.boxes is None or result.txts is None:
        print("No text detected.")
        image.show()
        return []

    detected_boxes = []
    draw = ImageDraw.Draw(image)

    for bbox, text, confidence in zip(result.boxes, result.txts, result.scores):
        x1 = int(np.min(bbox[:, 0]))
        y1 = int(np.min(bbox[:, 1]))
        x2 = int(np.max(bbox[:, 0]))
        y2 = int(np.max(bbox[:, 1]))

        draw.rectangle((x1, y1, x2, y2), outline="green", width=2)

        normalized_bbox = [
            x1 / image_width,
            y1 / image_height,
            x2 / image_width,
            y2 / image_height
        ]

        detected_boxes.append({
            "type": "text",
            "bbox": normalized_bbox,
            "content": text
        })

    image.show()

    return detected_boxes

"""results = test_rapidocr("/Users/peytonrivers/Desktop/small5.png")
print(f"results: {results}")"""

"""image = Image.open("/Users/peytonrivers/Desktop/Screenshot 2026-10-20 at 12.26.18 PM.png.png")
buffer = io.BytesIO()

image.save(buffer, format="PNG")
decoded_bytes = buffer.getvalue()
encoded_bytes1 = base64.b64encode(decoded_bytes).decode("utf-8")
data = {"image_input": encoded_bytes1, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
response = requests.post("http://127.0.0.1:8000/image_process", json=data)
response = response.json()
boxes_details1 = response["boxes_details"]

image = Image.open("/Users/peytonrivers/Desktop/test23.png")
image.show()
buffer = io.BytesIO()
image.save(buffer, format="PNG")
decoded_bytes = buffer.getvalue()
encoded_bytes2 = base64.b64encode(decoded_bytes).decode("utf-8")
data = {"image_input": encoded_bytes2, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
response = requests.post("http://127.0.0.1:8000/image_process", json=data)
response = response.json()
boxes_details2 = response["boxes_details"]

encoded_bytes = pixel_image_cropping(encoded_bytes1=encoded_bytes1, encoded_bytes2=encoded_bytes2)
encoded_bytes, boxes_details = expand_image(encoded_bytes=encoded_bytes)
print(f"boxes details: {boxes_details}")
decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
buffer = io.BytesIO(decoded_bytes)
image = Image.open(buffer)
image.show()

image = Image.open("/Users/peytonrivers/Desktop/test24.png")
buffer = io.BytesIO()

image.save(buffer, format="PNG")
decoded_bytes = buffer.getvalue()
encoded_bytes1 = base64.b64encode(decoded_bytes).decode("utf-8")
encoded_bytes, boxes_details = expand_image(encoded_bytes1)
decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
buffer = io.BytesIO(decoded_bytes)
image = Image.open(buffer)
image.show()
print(f"boxes details: {boxes_details}")
print("--------------------------------------------------------------")

image = Image.open("/Users/peytonrivers/Desktop/test25.png")
buffer = io.BytesIO()

image.save(buffer, format="PNG")
decoded_bytes = buffer.getvalue()
encoded_bytes1 = base64.b64encode(decoded_bytes).decode("utf-8")
encoded_bytes, boxes_details = expand_image(encoded_bytes1)
decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
buffer = io.BytesIO(decoded_bytes)
image = Image.open(buffer)
image.show()
print(f"boxes details: {boxes_details}")
print("--------------------------------------------------------------")

image = Image.open("/Users/peytonrivers/Desktop/test26.png")
buffer = io.BytesIO()

image.save(buffer, format="PNG")
decoded_bytes = buffer.getvalue()
encoded_bytes1 = base64.b64encode(decoded_bytes).decode("utf-8")
encoded_bytes, boxes_details = expand_image(encoded_bytes1)
decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
buffer = io.BytesIO(decoded_bytes)
image = Image.open(buffer)
image.show()
print(f"boxes details: {boxes_details}")
print("--------------------------------------------------------------")"""