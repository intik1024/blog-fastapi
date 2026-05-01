from passlib.context import CryptContext
from jose import JWTError,jwt
from datetime import datetime,timedelta,timezone
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import models

SECRET_KEY='your-secret-key-here-change-it'
ALGORITHM='HS256'
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

def hash_password(password:str):
    if len(password.encode('utf-8'))>72:
        password=password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    if len(plain_password.encode('utf-8'))>72:
        plain_password=plain_password[:72]
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data:dict,expires_delta:timedelta=None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc)+expires_delta
    else:
        expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')


