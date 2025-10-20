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