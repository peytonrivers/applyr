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
    secret_key=SESSION_SECRET_KEY
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://applyr-12k0.onrender.com",
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

    try:
        google_sub = request.session.get("google_sub")
        if not google_sub:
            raise HTTPException(status_code=401, detail="User not authenticated")

        user = session.query(Users).filter(Users.google_sub == google_sub).first()

        if not user:
            raise HTTPException(status_code=401, detail="User does not exist")

        user.first_name = data.first_name
        user.last_name = data.last_name
        user.phone_number = data.phone_number
        user.signup_complete = True

        session.commit()
        session.refresh(user)

        return {"Success": True}

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()
