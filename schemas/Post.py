from typing import List,Optional
from pydantic import BaseModel
from datetime import datetime
from schemas.User import UserResponse
from schemas.tag import TagResponse

class PostsBase(BaseModel):
    title:str
    content:str

class PostCreate(PostsBase):
    tag_names:List[str]=[]
    pass

class PostResponse(PostsBase):
    id:int
    created_at:datetime
    updated_at:Optional[datetime]=None
    user_id:int
    author: Optional[UserResponse]=None
    views:int

class PostUpdate(BaseModel):
    title:Optional[str]=None
    content:Optional[str]=None
    tag_names:Optional[List[str]]=None