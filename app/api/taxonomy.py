from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.taxonomy import Tag
from app.schemas import TagCreate, TagOut
from app.api.auth.authorization import require_admin

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])

def generate_slug(text: str) -> str:
    return text.lower().strip().replace(" ", "-")

# tags

@router.get("/tags", response_model=List[TagOut])
async def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()

@router.get("/tags/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="tag not found")
    return tag

@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    slug = generate_slug(tag_in.name)
    if db.query(Tag).filter((Tag.name == tag_in.name) | (Tag.slug == slug)).first():
        raise HTTPException(status_code=400, detail="tag name or slug already exists")

    tag = Tag(name=tag_in.name, slug=slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.put("/tags/{tag_id}", response_model=TagOut)
async def update_tag(
    tag_id: int,
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="tag not found")

    slug = generate_slug(tag_in.name)
    existing = db.query(Tag).filter(
        (Tag.name == tag_in.name) | (Tag.slug == slug)
    ).filter(Tag.id != tag_id).first()

    if existing:
        raise HTTPException(status_code=400, detail="new tag name or slug already exists")

    tag.name = tag_in.name
    tag.slug = slug
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="tag not found")

    db.delete(tag)
    db.commit()
    return None