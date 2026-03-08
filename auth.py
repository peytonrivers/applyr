import httpx
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from database import session, Users

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
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/auth/google")
def login_page():
    query_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    url = f"{google_auth_url}?{urlencode(query_params)}"
    return RedirectResponse(url)

@router.get("/auth/google/callback")
async def retrieve_information(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
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
        information = await client.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})

        if information.status_code != 200:
            return RedirectResponse(url=f"{FRONTEND_URL}/error.html")
        
        google_user = information.json()
        google_sub = google_user.get("sub")
        email = google_user.get("email")
        picture = google_user.get("picture")
        
        try:
            user = session.query(Users).filter(Users.google_sub == google_sub).first()

            if not user:
                # New user - create account
                user = Users(
                    google_sub=google_sub,
                    email=email,
                    profile_photo_url=picture,
                    signup_complete=False,
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                # Existing user - update profile
                user.email = email
                user.profile_photo_url = picture
                session.commit()
            
            # Issue JWT token
            jwt_token = create_access_token({"sub": str(user.user_id)})
            
            # Redirect to frontend callback page with token
            signup_complete_str = "true" if user.signup_complete else "false"
            callback_url = f"{FRONTEND_URL}/auth-callback.html?token={jwt_token}&signup_complete={signup_complete_str}&user_id={user.user_id}"
            return RedirectResponse(url=callback_url, status_code=302)

        except Exception as e:
            session.rollback()
            return RedirectResponse(url=f"{FRONTEND_URL}/error.html")
    
