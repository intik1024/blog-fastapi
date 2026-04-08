from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List

class CommentBase(BaseModel):
    content:str
    post_id:int
    parent_id:Optional[int]=None

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id:int
    created_at:datetime
    user_id:int
    post_id:int
    parent_id:Optional[int]=None
    replies:List['CommentResponse']=[]
    class Config:
        from_attributes=True

class CommentUpdate(BaseModel):
    content: Optional[str]=None