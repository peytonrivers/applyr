import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlencode
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from database import Users, RefreshToken, get_db
from sqlalchemy.orm import Session

router = APIRouter()

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=20)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


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
        google_access_token = info.get("access_token")
        if not google_access_token:
            return RedirectResponse(url=f"{FRONTEND_URL}/error.html")

        userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
        information = await client.get(
            userinfo_url, headers={"Authorization": f"Bearer {google_access_token}"}
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

        access_token = create_access_token({"sub": str(user.user_id)})
        refresh_token = create_refresh_token({"sub": str(user.user_id)})

        db_refresh_token = RefreshToken(
            user_id=str(user.user_id),
            token=refresh_token,
            is_valid=True,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(db_refresh_token)
        db.commit()

        if user.signup_complete:
            redirect_url = f"{FRONTEND_URL}/complete.html"
        else:
            redirect_url = f"{FRONTEND_URL}/signup.html"
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie("access_token", access_token, httponly=True, samesite="none", secure=True, max_age=1200)
        response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="none", secure=True, max_age=604800)
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        print(f"Auth error: {e}")
        db.rollback()
        return RedirectResponse(url=f"{FRONTEND_URL}/error.html")


@router.post("/auth/refresh")
async def refresh_tokens(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return JSONResponse(status_code=401, content={"detail": "No refresh token"})

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid refresh token"})

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.is_valid == True,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

    if not db_token:
        return JSONResponse(status_code=401, content={"detail": "Refresh token has been rotated or invalidated"})

    db_token.is_valid = False
    db.commit()

    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id})

    new_db_token = RefreshToken(
        user_id=user_id,
        token=new_refresh_token,
        is_valid=True,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(new_db_token)
    db.commit()

    response = JSONResponse({"message": "Tokens refreshed"})
    response.set_cookie("access_token", new_access_token, httponly=True, samesite="none", secure=True, max_age=1200)
    response.set_cookie("refresh_token", new_refresh_token, httponly=True, samesite="none", secure=True, max_age=604800)
    return response