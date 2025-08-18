# File: app/routes/post_router_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import Post

router = APIRouter()

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: str = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Retrieve a list of all posts."""
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    """Create a new post."""
    post = Post(title=post_data.title, content=post_data.content)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a single post by ID."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# File: app/routes/user_router_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import User

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Retrieve a list of all users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    user = User(username=user_data.username, email=user_data.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user