
Copy

from fastapi import FastAPI, Depends, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from auth import router as auth_router
from dotenv import load_dotenv
import os
from database import Users, get_db
from pydantic import BaseModel
from sqlalchemy.orm import Session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://apply-r.com",
        "https://www.apply-r.com",
        "https://applyr-frontend.onrender.com",
        "https://applyr-12k0.onrender.com",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,   # required for cookies to work cross-domain
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


def get_current_user_id(token: str = Cookie(None)) -> str:
    """Reads the JWT from the HttpOnly cookie set after Google OAuth."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/")
def root():
    return {"message": "ApplyR API is live"}


class SignupForm(BaseModel):
    first_name: str
    last_name: str
    phone_number: str


@app.post("/complete-signup")
def complete_signup(
    data: SignupForm,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.phone_number = data.phone_number
        user.signup_complete = True
        db.commit()
        db.refresh(user)

        return {
            "message": "Signup completed successfully",
            "user_id": user.user_id,
            "email": user.email,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")