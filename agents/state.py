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

class ClickAction(TypedDict):
    action: Literal["apply", "signup", "error"]
    index_number: int | None
    reason: str

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
    job_url: str
    company_name: str | None
    company_position: str | None

    # ── Forms Loop ─────────────────────────────────
    total_pages: int | None
    current_page: int
    questions: list[dict]
    errors: list[dict]

    # ── Signup ─────────────────────────────────────
    verification_code: str | None

    # ── Routing ────────────────────────────────────
    current_page: dict
    retry_count: int

    front_page: str
    ai_decision: ClickAction

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