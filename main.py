from fastapi import FastAPI, Depends,HTTPException,Form
from fastapi.params import Query
from sqlalchemy.orm import Session
from models.database import SessionLocal,engine
from models import models
from auth import oauth2_scheme,hash_password, verify_password, create_access_token,SECRET_KEY,ALGORITHM,JWTError
from sqlalchemy import or_
from schemas.User import UserCreate,UserResponse
from schemas.Post import PostCreate, PostResponse,PostUpdate
from schemas.Comment import CommentCreate,CommentResponse,CommentUpdate
from typing import List
from schemas.tag import TagCreate,TagResponse,TagUpdate
from jose import jwt
from fastapi import status

app=FastAPI()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    credentials_exception=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate':'Bearer'},
        )
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username==username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post('/users',response_model=UserResponse)
def create_users(user:UserCreate,db:Session=Depends(get_db)):
    existing=db.query(models.User).filter(
        or_(models.User.username==user.username,models.User.email==user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400,detail='User already exists')
    hashed_password=hash_password(user.password)
    db_user=models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
@app.post('/login')
def login(db:Session=Depends(get_db),username:str=Form(...),password:str=Form(...)):
    user =db.query(models.User).filter(
         models.User.username==username).first()

    if not user or not verify_password(password,user.password_hash):
        raise HTTPException(status_code=400,detail='Invalid username password')

    access_token=create_access_token(data={'sub':user.username})

    return {'access_token':access_token,'token_type':'bearer'}

@app.get('/users/me')
def read_users_me(current_user:models.User=Depends(get_current_user)):
    return {
        'id':current_user.id,
        'username':current_user.username,
        'email':current_user.email
    }
@app.post('/posts',response_model=PostResponse)
def create_post(post:PostCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    db_posts=models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
        views=0
    )
    for tag_name in post.tag_names:
        tag=db.query(models.Tag).filter(models.Tag.name==tag_name).first()
        if not tag:
            tag=models.Tag(name=tag_name)
            db.add(tag)
            db.flush()
        db_posts.tags.append(tag)
    db.add(db_posts)
    db.commit()
    db.refresh(db_posts)
    return db_posts

@app.get('/posts',response_model=List[PostResponse])
def read_posts(db:Session=Depends(get_db),skip:int = Query(0,ge=0,description='Сколько постов пропустить'),limit:int=Query(10,ge=1,le=100,description='Сколько вернуть')):
    query=db.query(models.Post)
    query=query.order_by(models.Post.created_at.desc())
    return query.offset(skip).limit(limit).all()

@app.get('/posts/{post_id}',response_model=PostResponse)
def read_post(post_id:int,db:Session=Depends(get_db)):
    db_post=db.query(models.Post).filter(models.Post.id==post_id).first()
    if not db_post:
        raise HTTPException(status_code=404,detail='Post not found')
    return db_post
@app.patch('/posts/{post_id}',response_model=PostResponse)
def update_post(post_id:int,post_update:PostUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    db_post=db.query(models.Post).filter(models.Post.id==post_id).first()
    if not db_post:
        raise HTTPException(status_code=404,detail='Post not found')

    if db_post.user_id!=current_user.id:
        raise HTTPException(status_code=403,detail='Not enough permission')

    if post_update.title is not None:
        db_post.title=post_update.title
    if post_update.content is not None:
        db_post.content=post_update.content

    if post_update.tag_names is not None:
        db_post.tags.clear()
        for tag_name in post_update.tag_names:
            tag=db.query(models.Tag).filter(models.Tag.name==tag_name).first()
            if not tag:
                tag=models.Tag(name=tag_name)
                db.add(tag)
                db.flush()
            db_post.tags.append(tag)

    db.commit()
    db.refresh(db_post)
    return db_post
@app.delete('/posts/{post_id}')
def delete_post(post_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    db_post=db.query(models.Post).filter(models.Post.id==post_id).first()
    if not db_post:
        raise HTTPException(status_code=404,detail='Post not found')
    if db_post.user_id!=current_user.id:
        raise HTTPException(status_code=403,detail='Not enough permission')

    db.delete(db_post)
    db.commit()
    return {'message':'Post deleted'}


@app.post('/posts/{id}/comments')
def create_comment(id:int,comment:CommentCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    parent_id=comment.parent_id if comment.parent_id!=0 else None

    db_comment=models.Comment(
        content=comment.content,
        user_id=current_user.id,
        post_id=id,
        parent_id=parent_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get('/posts/{id}/comments',response_model=List[CommentResponse])
def read_comments(id:int,db:Session=Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.post_id==id).all()

@app.get('/search',response_model=List[PostResponse])
def search_posts(q:str=Query(...,min_length=1,description='Поисковой запрос'),db:Session=Depends(get_db)):
    posts=db.query(models.Post).filter(
        or_(
            models.Post.title.ilike(f'%{q}%'),
            models.Post.content.ilike(f'%{q}%')
        )
    ).order_by(models.Post.created_at.desc()).all()
    return posts
@app.get('/comments/{id}',response_model=CommentResponse)
def read_comment(id:int,db:Session=Depends(get_db)):
    db_comment=db.query(models.Comment).filter(models.Comment.id==id).first()
    if not db_comment:
        raise HTTPException(status_code=404,detail='Comment not found')
    return db_comment

@app.patch('/comments/{id}',response_model=CommentResponse)
def update_comment(id:int,comment_update:CommentUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    db_comment=db.query(models.Comment).filter(models.Comment.id==id).first()
    if not db_comment:
        raise HTTPException(status_code=404,detail='COMMENT NOT FOUND')

    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403,detail='Not enough permission')

    if comment_update.content is not None:
        db_comment.content=comment_update.content

    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete('/comments/{id}')
def delete_comment(id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    db_comment=db.query(models.Comment).filter(models.Comment.id==id).first()
    if not db_comment:
        raise HTTPException(status_code=404,detail='Comment not found')
    if db_comment.user_id!=current_user.id:
        raise HTTPException(status_code=403,detail='Not enough permission')
    db.delete(db_comment)
    db.commit()
    return {'message':'Comment deleted'}

@app.post('/comments/{id}/replies')
def otvet_comment(id:int,comment:CommentCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    parent_comment=db.query(models.Comment).filter(models.Comment.id==id).first()
    if not parent_comment:
        raise HTTPException(status_code=404,detail='Parent comment not found')
    db_otvet=models.Comment(
        content=comment.content,
        user_id=current_user.id,
        post_id=parent_comment.post_id,
        parent_id=id
    )
    db.add(db_otvet)
    db.commit()
    db.refresh(db_otvet)
    return db_otvet

@app.get('/comments/{id}/replies',response_model=List[CommentResponse])
def read_otvet_comment(id:int,db:Session=Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.parent_id==id).all()

@app.post('/tags',response_model=TagResponse)
def create_tag(tag:TagCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403,detail='Not enought permission')

    existing=db.query(models.Tag).filter(models.Tag.name==tag.name).first()
    if existing:
        raise HTTPException(status_code=400,detail='Tag already exists')
    db_tag=models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.get('/tags',response_model=List[TagResponse])
def get_tags(db:Session=Depends(get_db)):
    return db.query(models.Tag).all()

@app.get('/tags/{tag_id}',response_model=TagResponse)
def get_tag(tag_id:int,db:Session=Depends(get_db)):
    tag=db.query(models.Tag).filter(models.Tag.id==tag_id).first()
    if not tag:
        raise HTTPException(status_code=404,detail='Tag not found')
    return tag

@app.patch('/tags/{tag_id}',response_model=TagResponse)
def update_tag(tag_id:int,tag_update:TagUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403,detail='Not enough permission')

    tag=db.query(models.Tag).filter(models.Tag.id==tag_id).first()
    if not tag:
        raise HTTPException(status_code=404,detail='Tag not found')

    if tag_update.name is not None:
        tag.name=tag_update.name

    db.commit()
    db.refresh(tag)
    return tag

@app.delete('/tags/{tag_id}')
def delete_tag(tag_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403,detail='Not enough permission')

    tag=db.query(models.Tag).filter(models.Tag.id==tag_id).first()
    if not tag:
        raise HTTPException(status_code=404,detail='Tag not found')

    db.delete(tag)
    db.commit()
    return {'message':'Tag deleted'}

@app.get('/posts/by-tag/{tag_name}',response_model=List[PostResponse])
def get_posts_by_tag(tag_name:str,db:Session=Depends(get_db)):
    tag=db.query(models.Tag).filter(models.Tag.name==tag_name).first()
    if not tag:
        raise HTTPException(status_code=404,detail='Tag not found')

    return tag.posts


if __name__ == "__main__":
    import uvicorn
    models.Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)

