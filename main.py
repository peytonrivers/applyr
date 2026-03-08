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

app = Fa