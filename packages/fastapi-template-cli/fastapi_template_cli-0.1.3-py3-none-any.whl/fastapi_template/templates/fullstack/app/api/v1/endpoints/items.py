"""
Item management endpoints.
"""

from typing import Any, List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app import crud, schemas
from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[schemas.Item])
def read_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve items for the current user.
    
    Args:
        db: Database session
        skip: Number of items to skip
        limit: Maximum number of items to return
        current_user: Current authenticated user
        
    Returns:
        List of items
    """
    if crud.user.is_superuser(current_user):
        items = crud.item.get_multi(db, skip=skip, limit=limit)
    else:
        items = crud.item.get_multi_by_owner(
            db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return items


@router.post("/", response_model=schemas.Item)
def create_item(
    *,
    db: Session = Depends(get_db),
    item_in: schemas.ItemCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new item.
    
    Args:
        db: Database session
        item_in: Item creation data
        current_user: Current authenticated user
        
    Returns:
        Created item
    """
    item = crud.item.create_with_owner(
        db, obj_in=item_in, owner_id=current_user.id
    )
    return item


@router.put("/{id}", response_model=schemas.Item)
def update_item(
    *,
    db: Session = Depends(get_db),
    id: int,
    item_in: schemas.ItemUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an item.
    
    Args:
        db: Database session
        id: Item ID
        item_in: Item update data
        current_user: Current authenticated user
        
    Returns:
        Updated item
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get("/{id}", response_model=schemas.Item)
def read_item(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get item by ID.
    
    Args:
        db: Database session
        id: Item ID
        current_user: Current authenticated user
        
    Returns:
        Item
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.delete("/{id}", response_model=schemas.Item)
def delete_item(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete an item.
    
    Args:
        db: Database session
        id: Item ID
        current_user: Current authenticated user
        
    Returns:
        Deleted item
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = crud.item.remove(db=db, id=id)
    return item