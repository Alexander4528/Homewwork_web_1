Код:
Main:
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes import router
from .storage import storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - создаем тестового пользователя если нужно
    print("Blog API started!")
    
    # Создаем тестового пользователя если нет пользователей
    if len(storage.users) == 0:
        try:
            test_user_data = {
                "email": "author@blog.com",
                "login": "blogauthor", 
                "password": "blogpass123"
            }
            storage.create_user(test_user_data)
            print("✓ Created test user: blogauthor (author@blog.com)")
        except Exception as e:
            print(f"✗ Error creating test user: {e}")
    
    print(f"✓ Loaded {len(storage.users)} users and {len(storage.posts)} posts")
    yield
    # Shutdown
    print("Blog API shutting down...")

app = FastAPI(
    title="Blog API",
    description="A simple blog platform with REST API",
    version="1.0.0",
    lifespan=lifespan
)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "users": len(storage.users), "posts": len(storage.posts)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
models:
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
import re

class User(BaseModel):
    id: int
    email: str
    login: str
    password: str
    createdAt: datetime
    updatedAt: datetime

class UserCreate(BaseModel):
    email: str
    login: str
    password: str
    
    @validator('login')
    def validate_login(cls, v):
        if len(v) < 3:
            raise ValueError('Login must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Login can only contain letters, numbers and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v

class UserUpdate(BaseModel):
    email: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None

class Post(BaseModel):
    id: int
    authorId: int
    title: str
    content: str
    createdAt: datetime
    updatedAt: datetime

class PostCreate(BaseModel):
    authorId: int
    title: str
    content: str
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1:
            raise ValueError('Title cannot be empty')
        if len(v) > 100:
            raise ValueError('Title cannot be longer than 100 characters')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) < 1:
            raise ValueError('Content cannot be empty')
        return v

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
routes:
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
@router.get("/create-user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@router.post("/create-user", response_class=HTMLResponse)
async def create_user_handler(
    request: Request,
    email: str = Form(...),
    login: str = Form(...),
    password: str = Form(...)
):
    try:
        user_data = UserCreate(email=email, login=login, password=password)
        storage.create_user(user_data.dict())
        return templates.TemplateResponse("create_user.html", {
            "request": request,
            "message": "User created successfully!"
        })
    except Exception as e:
        return templates.TemplateResponse("create_user.html", {
            "request": request,
            "error": str(e)
        })
@router.get("/create-user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@router.post("/create-user", response_class=HTMLResponse)
async def create_user_handler(
    request: Request,
    email: str = Form(...),
    login: str = Form(...),
    password: str = Form(...)
):
    try:
        # Проверяем, нет ли уже пользователя с таким email или login
        for user in storage.get_all_users():
            if user.email == email:
                return templates.TemplateResponse("create_user.html", {
                    "request": request,
                    "error": "Email already registered"
                })
            if user.login == login:
                return templates.TemplateResponse("create_user.html", {
                    "request": request,
                    "error": "Login already taken"
                })
        
        user_data = {
            "email": email,
            "login": login,
            "password": password
        }
        storage.create_user(user_data)
        
        return templates.TemplateResponse("create_user.html", {
            "request": request,
            "message": "User created successfully!"
        })
    except Exception as e:
        return templates.TemplateResponse("create_user.html", {
            "request": request,
            "error": f"Error creating user: {str(e)}"
        })
storage:
import json
from typing import Dict, List, Optional
from datetime import datetime
from .models import User, Post

class Storage:
    def __init__(self, filename: str = "data.json"):
        self.filename = filename
        self.users: Dict[int, User] = {}
        self.posts: Dict[int, Post] = {}
        self.next_user_id = 1
        self.next_post_id = 1
        self.load_from_file()
    
    def save_to_file(self):
        data = {
            "users": {str(k): v.dict() for k, v in self.users.items()},
            "posts": {str(k): v.dict() for k, v in self.posts.items()},
            "next_user_id": self.next_user_id,
            "next_post_id": self.next_post_id
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, default=str, indent=2)
    
    def load_from_file(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                
            # Load users
            for user_id, user_data in data.get("users", {}).items():
                user_data['createdAt'] = datetime.fromisoformat(user_data['createdAt'])
                user_data['updatedAt'] = datetime.fromisoformat(user_data['updatedAt'])
                self.users[int(user_id)] = User(**user_data)
            
            # Load posts
            for post_id, post_data in data.get("posts", {}).items():
                post_data['createdAt'] = datetime.fromisoformat(post_data['createdAt'])
                post_data['updatedAt'] = datetime.fromisoformat(post_data['updatedAt'])
                self.posts[int(post_id)] = Post(**post_data)
            
            self.next_user_id = data.get("next_user_id", 1)
            self.next_post_id = data.get("next_post_id", 1)
        except FileNotFoundError:
            # File doesn't exist yet, start with empty storage
            pass
    
    # User CRUD operations
    def create_user(self, user_data: dict) -> User:
        now = datetime.now()
        user = User(
            id=self.next_user_id,
            createdAt=now,
            updatedAt=now,
            **user_data
        )
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        self.save_to_file()
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        return list(self.users.values())
    
    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        update_data = user_data.copy()
        update_data['updatedAt'] = datetime.now()
        
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        
        self.save_to_file()
        return user
    
    def delete_user(self, user_id: int) -> bool:
        if user_id in self.users:
            # Also delete user's posts
            posts_to_delete = [post_id for post_id, post in self.posts.items() 
                             if post.authorId == user_id]
            for post_id in posts_to_delete:
                del self.posts[post_id]
            
            del self.users[user_id]
            self.save_to_file()
            return True
        return False
    
    # Post CRUD operations
    def create_post(self, post_data: dict) -> Post:
        now = datetime.now()
        post = Post(
            id=self.next_post_id,
            createdAt=now,
            updatedAt=now,
            **post_data
        )
        self.posts[self.next_post_id] = post
        self.next_post_id += 1
        self.save_to_file()
        return post
    
    def get_post(self, post_id: int) -> Optional[Post]:
        return self.posts.get(post_id)
    
    def get_all_posts(self) -> List[Post]:
        return list(self.posts.values())
    
    def get_user_posts(self, user_id: int) -> List[Post]:
        return [post for post in self.posts.values() if post.authorId == user_id]
    
    def update_post(self, post_id: int, post_data: dict) -> Optional[Post]:
        if post_id not in self.posts:
            return None
        
        post = self.posts[post_id]
        update_data = post_data.copy()
        update_data['updatedAt'] = datetime.now()
        
        for key, value in update_data.items():
            if value is not None:
                setattr(post, key, value)
        
        self.save_to_file()
        return post
    
    def delete_post(self, post_id: int) -> bool:
        if post_id in self.posts:
            del self.posts[post_id]
            self.save_to_file()
            return True
        return False

# Global storage instance
storage = Storage()
run:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
requirements:
txt
fastapi==0.104.1
uvicorn==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
