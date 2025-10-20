from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from .models import User, UserCreate, UserUpdate, Post, PostCreate, PostUpdate
from .storage import storage

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# HTML Routes
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    posts = storage.get_all_posts()
    # Enrich posts with author information
    enriched_posts = []
    for post in posts:
        author = storage.get_user(post.authorId)
        enriched_posts.append({
            **post.dict(),
            "author_login": author.login if author else "Unknown"
        })
    return templates.TemplateResponse("index.html", {"request": request, "posts": enriched_posts})

@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def read_post(request: Request, post_id: int):
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    author = storage.get_user(post.authorId)
    return templates.TemplateResponse("post.html", {
        "request": request, 
        "post": post,
        "author": author
    })

@router.get("/create-post", response_class=HTMLResponse)
async def create_post_form(request: Request):
    users = storage.get_all_users()
    return templates.TemplateResponse("create_post.html", {
        "request": request, 
        "users": users
    })

@router.get("/edit-post/{post_id}", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: int):
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return templates.TemplateResponse("edit_post.html", {
        "request": request, 
        "post": post
    })

# API Routes - Users
@router.post("/api/users/", response_model=User)
async def create_user(user: UserCreate):
    # Check if email or login already exists
    for existing_user in storage.get_all_users():
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_user.login == user.login:
            raise HTTPException(status_code=400, detail="Login already taken")
    
    return storage.create_user(user.dict())

@router.get("/api/users/", response_model=List[User])
async def read_users():
    return storage.get_all_users()

@router.get("/api/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    updated_user = storage.update_user(user_id, user.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    if not storage.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# API Routes - Posts
@router.post("/api/posts/", response_model=Post)
async def create_post(post: PostCreate):
    # Verify author exists
    author = storage.get_user(post.authorId)
    if not author:
        raise HTTPException(status_code=400, detail="Author not found")
    
    return storage.create_post(post.dict())

@router.get("/api/posts/", response_model=List[Post])
async def read_posts():
    return storage.get_all_posts()

@router.get("/api/posts/{post_id}", response_model=Post)
async def read_post(post_id: int):
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/api/users/{user_id}/posts", response_model=List[Post])
async def read_user_posts(user_id: int):
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return storage.get_user_posts(user_id)

@router.put("/api/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, post: PostUpdate):
    updated_post = storage.update_post(post_id, post.dict(exclude_unset=True))
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post

@router.delete("/api/posts/{post_id}")
async def delete_post(post_id: int):
    if not storage.delete_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

# HTML Form handlers
@router.post("/create-post", response_class=HTMLResponse)
async def create_post_handler(
    request: Request,
    authorId: int = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    post_data = PostCreate(authorId=authorId, title=title, content=content)
    storage.create_post(post_data.dict())
    posts = storage.get_all_posts()
    enriched_posts = []
    for post in posts:
        author = storage.get_user(post.authorId)
        enriched_posts.append({
            **post.dict(),
            "author_login": author.login if author else "Unknown"
        })
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "posts": enriched_posts,
        "message": "Post created successfully!"
    })

@router.post("/edit-post/{post_id}", response_class=HTMLResponse)
async def edit_post_handler(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...)
):
    post_data = PostUpdate(title=title, content=content)
    updated_post = storage.update_post(post_id, post_data.dict(exclude_unset=True))
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = storage.get_post(post_id)
    author = storage.get_user(post.authorId)
    return templates.TemplateResponse("post.html", {
        "request": request, 
        "post": post,
        "author": author,
        "message": "Post updated successfully!"
    })