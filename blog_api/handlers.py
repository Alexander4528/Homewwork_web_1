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