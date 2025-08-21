"""
User management endpoints.
"""

from typing import Any, List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from app import crud, schemas
from app.api.deps import get_current_active_superuser, get_current_active_user
from app.db.database import get_db
from app.models.user import User

router = APIRouter()
security = HTTPBearer()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users (admin only).
    
    Args:
        db: Database session
        skip: Number of users to skip
        limit: Maximum number of users to return
        current_user: Current authenticated user
        
    Returns:
        List of users
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new user (admin only).
    
    Args:
        db: Database session
        user_in: User creation data
        current_user: Current authenticated user
        
    Returns:
        Created user
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Current user
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by ID.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    password: str = None,
    full_name: str = None,
    email: str = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    
    Args:
        db: Database session
        password: New password
        full_name: New full name
        email: New email
        current_user: Current authenticated user
        
    Returns:
        Updated user
    """
    current_user_data = schemas.User(**current_user.__dict__)
    user_in = schemas.UserUpdate(**current_user_data.dict())
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user