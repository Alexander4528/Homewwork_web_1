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