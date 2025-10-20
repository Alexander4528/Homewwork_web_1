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