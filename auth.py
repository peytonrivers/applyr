import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from database import Users, get_db
from sqlalchemy.orm import Session

router = APIRouter()

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.get("/auth/google")
def login_page():
    query_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(query_params)}"
    return RedirectResponse(url)


@router.get("/auth/google/callback")
async def retrieve_information(code: str, db: Session = Depends(get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        client_data = await client.post(token_url, data=data)
        if client_data.status_code != 200:
            return RedirectResponse(url=f"{FRONTEND_URL}/error.html")

        info = client_data.json()
        access_token = info.get("access_token")
        if not access_token:
            return RedirectResponse(url=f"{FRONTEND_URL}/error.html")

        userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
        information = await client.get(
            userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
        )
        if information.status_code != 200:
            return RedirectResponse(url=f"{FRONTEND_URL}/error.html")

        google_user = information.json()
        google_sub = google_user.get("sub")
        email = google_user.get("email")
        picture = google_user.get("picture")

    try:
        user = db.query(Users).filter(Users.google_sub == google_sub).first()

        if not user:
            user = Users(
                google_sub=google_sub,
                email=email,
                profile_photo_url=picture,
                signup_complete=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.email = email
            user.profile_photo_url = picture
            db.commit()

        jwt_token = create_access_token({"sub": str(user.user_id)})
        signup_complete_str = "true" if user.signup_complete else "false"

        # Token in URL — frontend reads it, stores in sessionStorage, wipes from URL
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth-callback.html?token={jwt_token}&signup_complete={signup_complete_str}",
            status_code=302,
        )

    except Exception:
        db.rollback()
        return RedirectResponse(url=f"{FRONTEND_URL}/error.html")