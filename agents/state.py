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
from langgraph.graph.message import add_messages

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

class ApplicationState(TypedDict):
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
