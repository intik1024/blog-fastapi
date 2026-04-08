from pydantic import BaseModel,EmailStr
from datetime import datetime

class UsersBase(BaseModel):
    username:str
    email:EmailStr

class UserCreate(UsersBase):
    password:str

class UserResponse(UsersBase):
    id:int
    is_admin:bool=False
    created_at:datetime

    class Config:
        from_attributes=True
