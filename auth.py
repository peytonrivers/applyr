import httpx
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import httpx
from database import session, Users

router = APIRouter()

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

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
async def retrieve_information(code: str, request: Request):
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
            return RedirectResponse(url="http://127.0.0.1:5500/error.html", status_code=302)
        
        info =  client_data.json()
        access_token = info.get("access_token")
        if not access_token:
            return RedirectResponse(url="http://127.0.0.1:5500/error.html", status_code=302)
        
        userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
        information = await client.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})

        if information.status_code != 200:
            return RedirectResponse(url="http://127.0.0.1:5500/error.html", status_code=302)
        
        client_lis = information.json()
        google_sub = client_lis.get("sub")
        email = client_lis.get("email")
        picture = client_lis.get("picture")
        finish_signup = "http://127.0.0.1:5500/signup.html"
        request.session["google_sub"] = google_sub
        try:
            user = session.query(Users).filter(Users.google_sub == google_sub).first()

            if not user:
                user = Users(
                    google_sub=google_sub,
                    email=email,
                    profile_photo_url=picture,
                    signup_complete=False,
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            
            elif user.signup_complete == True:
                user.email = email
                user.profile_photo_url = picture
                session.commit()
                return RedirectResponse(url="http://127.0.0.1:5500/complete.html")

            else:
                user.email = email
                user.profile_photo_url = picture
                session.commit()

        except Exception as e:
            session.rollback()
            return RedirectResponse(url="http://127.0.0.1:5500/error.html", status_code=302)

        finally:
            session.close()

        return RedirectResponse(url="http://127.0.0.1:5500/signup.html")
    
