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