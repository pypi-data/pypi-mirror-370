"""
User Pydantic schemas.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """User creation schema."""
    
    email: EmailStr
    username: str
    password: str


class UserUpdate(UserBase):
    """User update schema."""
    
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Base user schema with ID."""
    
    id: Optional[int] = None
    
    class Config:
        orm_mode = True


class User(UserInDBBase):
    """User schema for responses."""
    pass


class UserInDB(UserInDBBase):
    """User schema with hashed password."""
    
    hashed_password: str