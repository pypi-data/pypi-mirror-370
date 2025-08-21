"""
Item Pydantic schemas.
"""

from typing import Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    """Base item schema."""
    
    title: str
    description: Optional[str] = None
    price: float
    is_available: bool = True


class ItemCreate(ItemBase):
    """Item creation schema."""
    pass


class ItemUpdate(BaseModel):
    """Item update schema."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None


class ItemInDBBase(ItemBase):
    """Base item schema with ID."""
    
    id: int
    owner_id: int
    
    class Config:
        orm_mode = True


class Item(ItemInDBBase):
    """Item schema for responses."""
    pass