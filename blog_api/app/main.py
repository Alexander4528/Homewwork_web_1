from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes import router
from .storage import storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Blog API started!")
    print(f"Loaded {len(storage.users)} users and {len(storage.posts)} posts")
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