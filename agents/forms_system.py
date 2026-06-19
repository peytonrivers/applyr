from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess
from playwright.sync_api import sync_playwright

from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")
llm = ChatOpenAI(model="gpt-5.4-nano", temperature=0.3, api_key=OPENAI_KEY)

def get_all_elements(state: ApplicationState):
    page = state["current_page"]["page"]
    interactive_elements = "input, button, select, button, select, datalist, role, aria-label"
    clickables = page.locator(interactive_elements)
    all_elements = []
    for i in range(clickables.count()):
        element = clickables.nth(i)
        tag = element.evaluate("el.tagName.toLowerCase()")
        index = i
        raw_text = element.text_content() or ""
        element_text = raw_text.strip()
        element_id = element.get_attribute("id")
        label_text = ""
        
        if element_id:
            label = page.locator(f'[for="{element_id}"]')
            if label.count() > 0:
                raw_label_text = label.text_content() or ""
                label_text = raw_label_text.strip()
        element_attributes = element.evaluate("""
        el => {
                let elementAttribute = [];
                for (const attr of el.attributes) {
                    elementAttribute.push({ name: attr.name, value: attr.value });
                }
                return elementAttribute;
            }
        """)
        data = {
            "tag": tag,
            "index": index,
            "element_id": element_id,
            "text": element_text,
            "label_text": label_text,
            "element_attributes": element_attributes
        }
        all_elements.append(data)
    state["all_elements"] = all_elements
    return state


    