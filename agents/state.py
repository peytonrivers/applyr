# LangGraph Agent to start the Application
"""
    1. Open the URL
    2. 404 error or Timeout
        - break & set the url to inactive
    3. Track Domain inside of url
    4. Find Apply Button
        - HTML Scraping
        - Looking for buttons as well
    5. Click Apply with playwright apply tool
        - If 404 Error or Timeout
            - break & set the url to inactive
        - If Not the same Domain
            - break & est the url to inactive
    6. Send to Recognition Tool
"""

from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage, AIMessage, HumanMessage, ToolMessage
from playwright.sync_api import Locator

class FormsAction(TypedDict):
    action: Literal[
        "fill_text",
        "choose_options",
        "check_box",
        "click_button",
        "upload_resume",
        "upload_cover_letter",
        "open_more_context",
        "skip"
    ]
    answer: str | None
    option_answer_index: list[int] | None
    needs_options: bool
    needs_parent_elements: bool
    needs_sister_elements: bool
    needs_children_elements: bool
    reason: str

class SignupProcess(TypedDict):
    input_indexes: list[int] | None
    input_indexes_reason: str
    radio_indexes: list[int] | None
    radio_indexes_reason: str
    checkbox_indexes: list[int] | None
    checkbox_indexes_reason: str
    select_indexes: list[int] | None
    select_indexes_reason: str
    datalist_indexes: list[int] | None
    datalist_indexes_reason: str
    follow_through_element: int | None
    follow_through_reason: str

class ApplyProcess(TypedDict):
    application_page: bool
    index_number: int | None
    reason: str

class DecidePage(TypedDict):
    action: Literal["apply", "signup", "forms", "cookies", "verification", "other", "error"]
    action_reason: str

class MultipleQuestionItem(TypedDict):
    label_text: str | None
    index: int | None


class MultipleQuestionGrouping(TypedDict):
    question: str
    grouping: str | None
    options: list[MultipleQuestionItem]


class MultipleQuestion(TypedDict):
    questions: list[str] | None
    needs_custom_grouping: bool
    custom_grouping: list[MultipleQuestionGrouping] | None

class AllElementsItem(TypedDict):
    question: str 
    index: int

class AllElementsGrouping(TypedDict):
    question: str
    option: list[AllElementsItem]


class AllElements(TypedDict):
    custom_grouping: list[AllElementsGrouping]
    follow_through_element: int | None
    follow_through_reason: str

class ClickAction(TypedDict):
    action: Literal["apply", "signup", "error"]
    index_number: int | None
    reason: str

class CurrentPage(TypedDict):
    page: str | None
    url: str | None
    browser: str | None
    context: str | None

class MiddlePageDecision(TypedDict):
    action: Literal["apply", "signup", "forms", "cookies", "other", "error"]
    action_reason: str

class CookiesProcess(TypedDict):
    follow_through_index: int | None
    follow_through_reason: str | None

class ApplicationState(TypedDict):
    # ── User Identity ──────────────────────────────
    user_id: str
    first_name: str
    last_name: str
    preferred_name: str | None
    email: str
    phone_number: str

    # ── Address ────────────────────────────────────
    address_line1: str | None
    address_line2: str | None
    city: str | None
    user_state: str | None
    zip_code: str | None
    country: str | None

    # ── Work Eligibility ───────────────────────────
    work_authorized: bool | None
    requires_sponsorship: bool | None
    veteran: bool | None
    disability: bool | None

    # ── Links ──────────────────────────────────────
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None

    # ── Documents ──────────────────────────────────
    resume_text: str
    resume_upload: str
    cover_letter_text: str | None
    cover_letter_upload: str | None

    # ── Job Info ───────────────────────────────────
    url: str
    company_name: str | None
    company_position: str | None

    # ── Forms Loop ─────────────────────────────────
    total_pages: int | None

    # ── Signup ─────────────────────────────────────
    verification_code: str | None

    # ── Routing ────────────────────────────────────
    current_page: CurrentPage
    retry_count: int

    previous_action: Literal["apply", "signup", "forms", "cookies", "verification", "other", "error"] | None
    signup_process: SignupProcess
    apply_process: ApplyProcess
    decide_page: DecidePage
    cookies_response: CookiesProcess
    front_page: str
    body_text: str
    ai_decision: ClickAction
    all_elements: list[dict]
    all_elements_clickables: Locator
    follow_through_element: dict
    follow_through_reason: str
    radio_elements: list[dict]
    radio_elements_clickables: Locator
    checkbox_elements: list[dict]
    checkbox_elements_clickables: Locator
    select_elements: list[dict]
    select_elements_clickables: Locator
    datalist_elements: list[dict]
    datalist_elements_clickables: Locator

    # ── Messages ───────────────────────────────────
    messages: Annotated[list[AnyMessage], add_messages]

def convert_to_system(state: ApplicationState):
    user_id = state["user_id"]
    first_name = state["first_name"]
    last_name = state["last_name"]
    preferred_name = state["preferred_name"]
    phone_number = state["phone_number"]
    email = state["email"]

    address_line1 = state["address_line1"]
    address_line2 = state["address_line2"]
    city = state["city"]
    user_state = state["user_state"]
    zip_code = state["zip_code"]
    country = state["country"]

    work_authorized = state["work_authorized"]
    requires_sponsorship = state["requires_sponsorship"]
    veteran = state["veteran"]
    disability = state["disability"]

    linkedin_url = state["linkedin_url"]
    github_url = state["github_url"]
    portfolio_url = state["portfolio_url"]

    resume_text = state["resume_text"]
    cover_letter_text = state["cover_letter_text"]

    company_name = state["company_name"]
    company_position = state["company_position"]
    job_url = state["job_url"]

    system_prompt = f"""You are an AI job application assistant filling out a job application on behalf of the user.

    ## User Profile
    - Name: {first_name} {last_name}
    - Preferred Name: {preferred_name or "N/A"}
    - Email: {email}
    - Phone: {phone_number}

    ## Address
    - {address_line1}{f", {address_line2}" if address_line2 else ""}
    - {city}, {user_state} {zip_code}
    - {country}

    ## Work Eligibility
    - Authorized to work: {work_authorized}
    - Requires sponsorship: {requires_sponsorship}
    - Veteran: {veteran}
    - Disability: {disability}

    ## Links
    - LinkedIn: {linkedin_url or "N/A"}
    - GitHub: {github_url or "N/A"}
    - Portfolio: {portfolio_url or "N/A"}

    ## Job
    - Company: {company_name}
    - Position: {company_position}
    - URL: {job_url}

    ## Resume
    {resume_text}

    ## Cover Letter
    {cover_letter_text or "N/A"}

    Use this information to accurately answer all questions in the job application.
    Always prefer the exact values provided. If a field is N/A, leave it blank or skip it.
    """
    state["messages"] = [SystemMessage(content=system_prompt)]

    return state

    


class UserProfile(TypedDict):
    # Identity
    first_name: str
    last_name: str
    email: str
    phone_number: str

    # Address
    address_line1: str | None
    city: str | None
    state: str | None
    zip_code: str | None

    # Work eligibility
    work_authorized: bool | None
    requires_sponsorship: bool | None

    # Links
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None

class ApplicationsState(TypedDict):
    # Required
    job_url: str
    user_id: str
    user_profile: UserProfile       # ← everything about the person lives here

    # Job info
    company_name: str | None
    job_type: str | None

    # Documents
    resume_text: str
    resume_upload: str
    cover_letter_text: str | None
    cover_letter_upload: str | None

    # Routing + state
    intent: Literal["apply", "recognition", "signup", "forms"] | None
    current_page_url: str | None
    error: str | None
    retry_count: int
    messages: Annotated[list, add_messages]

    # Classifications
    apply_classification: ApplyClassification | None
    recognition_classification: RecognitionClassification | None
    signup_classification: SignupClassification | None
    forms_classification: FormsClassification | None
    
class ApplyClassification(TypedDict):
    your: str
    button_found: bool | None
    need_ai_to_find_button: bool | None
    link_follow_through: bool | None

class RecognitionClassification(TypedDict):
    your: str
    link_follow_through: bool | None
    intent: Literal["apply", "recognition", "signup", "forms"] | None

class SignupClassification(TypedDict):
    your: str
    verification_code: str | None
    link_follow_through: bool | None


class FormsClassification(TypedDict):
    your: str
    questions_total: int | None
    current_questions_done: int | None
    link_follow_through: bool | None