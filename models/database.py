import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123@localhost/blog_db")

engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)