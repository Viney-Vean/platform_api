from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Item])
def read_items(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100,
               current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Retrieve items.
    """
    if crud.user_orm.is_superuser(current_user):
        items = crud.item_orm.get_multi(db, skip=skip, limit=limit)
    else:
        items = crud.item_orm.get_multi_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return items


@router.post("/", response_model=schemas.Item)
def create_item(*, db: Session = Depends(deps.get_db), item_in: schemas.ItemCreate,
                current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Create new item.
    """
    item = crud.item_orm.create_with_owner(db=db, obj_in=item_in, owner_id=current_user.id)
    return item


def validate_item(db, record_id, current_user):
    item = crud.item_orm.get(db=db, id=record_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not crud.user_orm.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return item


@router.put("/{record_id}", response_model=schemas.Item)
def update_item(*, db: Session = Depends(deps.get_db), record_id: int, item_in: schemas.ItemUpdate,
                current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Update an item.
    """
    item = validate_item(db, record_id, current_user)
    item = crud.item_orm.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get("/{record_id}", response_model=schemas.Item)
def read_item(*, db: Session = Depends(deps.get_db), record_id: int,
              current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Get item by ID.
    """
    item = validate_item(db, record_id, current_user)
    return item


@router.delete("/{record_id}", response_model=schemas.Item)
def delete_item(*, db: Session = Depends(deps.get_db), record_id: int,
                current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Delete an item.
    """
    validate_item(db, record_id, current_user)
    item = crud.item_orm.remove(db=db, id=record_id)
    return item
