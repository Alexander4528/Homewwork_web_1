Код:
Main:
from fastapi import FastAPI, HTTPException, Request
from models import User, Post
from handlers import (
    create_user, read_users, update_user, delete_user,
    create_post, read_posts, update_post, delete_post
)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

# CRUD для пользователей
@app.post("/users/")
async def api_create_user(user: User):
    return create_user(user)

@app.get("/users/")
async def api_read_users():
    return read_users()

@app.put("/users/{user_id}")
async def api_update_user(user_id: int, user: User):
    return update_user(user_id, user)

@app.delete("/users/{user_id}")
async def api_delete_user(user_id: int):
    delete_user(user_id)
    return {"detail": "User deleted"}

# CRUD для постов
@app.post("/posts/")
async def api_create_post(post: Post):
    return create_post(post)

@app.get("/posts/")
async def api_read_posts():
    return read_posts()

@app.put("/posts/{post_id}")
async def api_update_post(post_id: int, post: Post):
    return update_post(post_id, post)

@app.delete("/posts/{post_id}")
async def api_delete_post(post_id: int):
    delete_post(post_id)
    return {"detail": "Post deleted"}

@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def get_chrome_devtools():
    # Возвращайте нужные данные или пустой объект, если данных нет
    return {"message": "This is the com.chrome.devtools.json configuration"}
  
Models:
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    email: EmailStr
    login: str
    password: str
    createdAt: datetime
    updatedAt: datetime

class Post(BaseModel):
    id: int
    authorId: int
    title: str
    content: str
    createdAt: datetime
    updatedAt: datetime

Handlers:
from fastapi import HTTPException
from models import User, Post
from datetime import datetime
from storage import users, posts, save_data

# Helper functions
def get_user(user_id: int) -> User:
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

def get_post(post_id: int) -> Post:
    for post in posts:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

# CRUD for User
def create_user(user_data: User):
    if any(u.id == user_data.id for u in users):
        raise HTTPException(status_code=400, detail="User ID already exists")
    user_data.createdAt = datetime.utcnow()
    user_data.updatedAt = datetime.utcnow()
    users.append(user_data)
    save_data()
    return user_data

def read_users():
    return users

def update_user(user_id: int, user_data: User):
    user = get_user(user_id)
    user.email = user_data.email
    user.login = user_data.login
    user.password = user_data.password
    user.updatedAt = datetime.utcnow()
    save_data()
    return user

def delete_user(user_id: int):
    global users
    users = [u for u in users if u.id != user_id]
    save_data()

# CRUD for Post
def create_post(post_data: Post):
    if any(p.id == post_data.id for p in posts):
        raise HTTPException(status_code=400, detail="Post ID already exists")
    post_data.createdAt = datetime.utcnow()
    post_data.updatedAt = datetime.utcnow()
    posts.append(post_data)
    save_data()
    return post_data

def read_posts():
    return posts

def update_post(post_id: int, post_data: Post):
    post = get_post(post_id)
    post.title = post_data.title
    post.content = post_data.content
    post.updatedAt = datetime.utcnow()
    save_data()
    return post

def delete_post(post_id: int):
    global posts
    posts = [p for p in posts if p.id != post_id]
    save_data()
  
storage:
import json
from typing import List
from models import User, Post
from datetime import datetime

users: List[User] = []
posts: List[Post] = []

def save_data():
    with open('data.json', 'w') as f:
        json.dump({'users': [user.dict() for user in users],
                   'posts': [post.dict() for post in posts]}, f, default=str)

def load_data():
    global users, posts
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            users = [User(**u) for u in data.get('users', [])]
            posts = [Post(**p) for p in data.get('posts', [])]
    except FileNotFoundError:
        pass

load_data()

requirements:
fastapi
uvicorn
pydantic
typing_extensions
