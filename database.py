import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
import uuid
from uuid import uuid4
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(url=DATABASE_URL, echo=True)


Session = sessionmaker(bind=engine, autocommit=False)

session = Session()

Base = declarative_base()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

def gen_random_id():
    return str(uuid.uuid4())

class Users(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, nullable=False, default=gen_random_id)
    google_sub = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False, index=True)
    profile_photo_url = Column(String, nullable=True)
    first_name = Column(String, nullable=True, index=True)
    last_name = Column(String, nullable=True, index=True)
    phone_number = Column(String, nullable=True, index=True)
    signup_time = Column(DateTime, server_default=func.now(), nullable=True, index=True)
    signup_complete = Column(Boolean, nullable=True, server_default="false", index=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(String, primary_key=True, default=gen_random_id)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False)
    is_valid = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()