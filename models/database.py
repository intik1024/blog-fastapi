import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123@localhost/blog_db")

engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

redis_client=redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True,
    db=0
)