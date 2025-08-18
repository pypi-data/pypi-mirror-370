# File: app/main.py (updated with auth)
from fastapi import FastAPI
from .database import engine, Base
from . import models

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="FastAPI Application with Authentication",
    version="1.0.0",
    description="Generated API from blueprint specification with JWT authentication"
)

# Import and include routers
from .routes.auth_routes import router as auth_router
from .routes.post_router_routes import router as post_router
from .routes.user_router_routes import router as user_router

# Include authentication routes (public)
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Include other routes
app.include_router(post_router, prefix="/api/posts", tags=["posts"])
app.include_router(user_router, prefix="/api/users", tags=["users"])

# Health check endpoint
@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok", "message": "API is healthy"}

# Root endpoint
@app.get("/", summary="API Info")
def read_root():
    return {
        "message": "Welcome to the FastAPI Blueprint Generated API with Authentication",
        "docs": "/docs",
        "health": "/health",
        "auth": {
            "register": "/auth/register",
            "login": "/auth/login",
            "login-json": "/auth/login-json"
        }
    }