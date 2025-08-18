# File: app/crud.py (updated)
from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, obj_in: schemas.UserCreate):
    hashed_password = get_password_hash(obj_in.password)
    db_obj = models.User(
        username=obj_in.username,
        email=obj_in.email,
        hashed_password=hashed_password
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_user(db: Session, db_obj: models.User, obj_in: schemas.UserUpdate):
    obj_data = obj_in.dict(exclude_unset=True)
    
    # Handle password hashing if password is being updated
    if "password" in obj_data:
        hashed_password = get_password_hash(obj_data["password"])
        obj_data["hashed_password"] = hashed_password
        del obj_data["password"]  # Remove plain password
    
    for field, value in obj_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

# Post CRUD operations
def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def create_post(db: Session, obj_in: schemas.PostCreate):
    obj_data = obj_in.dict()
    db_obj = models.Post(**obj_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_post(db: Session, db_obj: models.Post, obj_in: schemas.PostUpdate):
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post