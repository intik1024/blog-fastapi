from sqlalchemy import Column,Integer,String,Text,Boolean,DateTime,ForeignKey,Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,backref
from models.database import Base


post_tags=Table('post_tags',
                Base.metadata,
                Column('post_id',Integer,ForeignKey('posts.id')),
                Column('tag_id',Integer,ForeignKey('tags.id'))
)

class User(Base):
    __tablename__='users'

    id=Column(Integer,primary_key=True,index=True)
    username=Column(String,unique=True,index=True,nullable=False)
    email=Column(String,unique=True,index=True,nullable=False)
    password_hash=Column(String,nullable=False)
    is_admin=Column(Boolean,default=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    posts=relationship('Post',back_populates='author')
    comments=relationship('Comment',back_populates='author')

class Post(Base):
    __tablename__='posts'

    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(200),nullable=False)
    content=Column(Text,nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
    views=Column(Integer,default=0)

    user_id=Column(Integer,ForeignKey('users.id'),nullable=False)

    author=relationship('User',back_populates='posts')
    comments=relationship('Comment',back_populates='post',cascade='all, delete-orphan')
    tags=relationship('Tag',secondary=post_tags,back_populates='posts')

class Comment(Base):
    __tablename__='comments'

    id=Column(Integer,primary_key=True,index=True)
    content=Column(Text,nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    user_id=Column(Integer,ForeignKey('users.id'),nullable=False)
    post_id=Column(Integer,ForeignKey('posts.id'),nullable=False)
    parent_id=Column(Integer,ForeignKey('comments.id'),nullable=True)

    author=relationship('User',back_populates='comments')
    post=relationship('Post',back_populates='comments')
    replies=relationship('Comment',backref=backref('parent',remote_side=[id]))

class Tag(Base):
    __tablename__='tags'

    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,unique=True,index=True,nullable=False)

    posts=relationship('Post',secondary=post_tags,back_populates='tags')
