from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from auth import router as auth_router
from dotenv import load_dotenv
import os
from database import session, Users
from pydantic import BaseModel
from fastapi import HTTPException
load_dotenv()

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    same_site="none",
    https_only=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://apply-r.com",
        "https://www.apply-r.com",
        "https://applyr-frontend.onrender.com",
        "https://applyr-frontend.onrender.com"
        "https://applyr-12k0.onrender.com",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "ApplyR API is live"}


class SignupForm(BaseModel):
    first_name: str
    last_name: str
    phone_number: str

@app.post("/complete-signup")
def complete_signup(data: SignupForm, request: Request):

    google_sub = request.session.get("google_sub")

    if not google_sub:
        return {
            "debug_step": "session_check_failed",
            "session": dict(request.session),
            "google_sub": google_sub
        }

    user = session.query(Users).filter(Users.google_sub == google_sub).first()

    if not user:
        return {
            "debug_step": "user_not_found",
            "google_sub": google_sub
        }

    try:
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.phone_number = data.phone_number
        user.signup_complete = True

        session.commit()
        session.refresh(user)

        return {
            "debug_step": "signup_success",
            "google_sub": google_sub,
            "user_id": user.user_id
        }

    except Exception as e:
        session.rollback()
        return {
            "debug_step": "database_error",
            "error": str(e)
        }

    finally:
        session.close()