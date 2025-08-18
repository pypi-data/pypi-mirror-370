# File: app/routes/user_router_routes.py (updated with auth)
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_active_user
from .. import crud, schemas, models

router = APIRouter()

@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user)  # Requires authentication
):
    """Retrieve a list of all users. (Protected route)"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_active_user)
):
    """Get current user's information."""
    return current_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)  # Requires authentication
):
    """Get a single user by ID. (Protected route)"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_data: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update current user's information."""
    # Check for email conflicts if email is being updated
    if user_data.email and user_data.email != current_user.email:
        existing_user = crud.get_user_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check for username conflicts if username is being updated
    if user_data.username and user_data.username != current_user.username:
        existing_user = crud.get_user_by_username(db, username=user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.update_user(db=db, db_obj=current_user, obj_in=user_data)

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int, 
    user_data: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)  # Requires authentication
):
    """Update an existing user. (Protected route)"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check for email conflicts if email is being updated
    if user_data.email and user_data.email != user.email:
        existing_user = crud.get_user_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check for username conflicts if username is being updated
    if user_data.username and user_data.username != user.username:
        existing_user = crud.get_user_by_username(db, username=user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.update_user(db=db, db_obj=user, obj_in=user_data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)  # Requires authentication
):
    """Delete a user. (Protected route)"""
    user = crud.delete_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")