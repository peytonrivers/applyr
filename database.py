import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
import uuid
from uuid import uuid4


username = "peytonrivers"
host = "localhost"
port = 5432
database_name = "applyrdb"


engine = create_engine(f"postgresql+psycopg2://{username}:password@{host}:{port}/{database_name}", echo=True)

Session = sessionmaker(bind=engine, autocommit=False)

session = Session()

Base = declarative_base()


def gen_random_id():
    return str(uuid.uuid4())

class Users(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, nullable=False, default=gen_random_id)
    google_sub = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False, index=True)
    profile_photo_url = Column(String, nullable=True)
    first_name = Column(String, nullable=True,index=True)
    last_name = Column(String, nullable=True, index=True)
    phone_number = Column(String, nullable=True, index=True)
    signup_time = Column(DateTime, server_default=func.now(), nullable=True, index=True)
    signup_complete = Column(Boolean, nullable=True, server_default="false", index=True)



def init_db():
    Base.metadat