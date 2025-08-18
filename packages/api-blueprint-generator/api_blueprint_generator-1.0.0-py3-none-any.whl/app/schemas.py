# File: app/schemas.py (updated)
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Post schemas
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(PostBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Generic response schemas
class Message(BaseModel):
    message: str

class HTTPError(BaseModel):
    detail: str