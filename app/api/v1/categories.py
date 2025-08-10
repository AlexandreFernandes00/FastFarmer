from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...models.catalog import Category
from ...schemas.category import CategoryRead

router = APIRouter()

@router.get("/", response_model=list[CategoryRead])
def list_categories(type: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Category)
    if type:
        q = q.filter(Category.type == type)
    return q.order_by(Category.type, Category.name).all()
