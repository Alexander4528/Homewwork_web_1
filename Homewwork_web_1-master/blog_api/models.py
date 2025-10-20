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