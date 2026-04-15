import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag = Tag(
        user_id=user.id,
        name=data.name,
        color=data.color,
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    result = await db.execute(
        select(Tag).where(Tag.id == tag.id).options(selectinload(Tag.subscriptions))
    )
    tag = result.scalar_one()
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        subscription_count=len(tag.subscriptions),
    )


@router.get("/", response_model=list[TagResponse])
async def list_tags(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Tag)
        .where(Tag.user_id == user.id)
        .options(selectinload(Tag.subscriptions))
        .order_by(Tag.created_at.asc())
    )
    tags = result.scalars().all()
    return [
        TagResponse(
            id=t.id,
            name=t.name,
            color=t.color,
            subscription_count=len(t.subscriptions),
        )
        for t in tags
    ]


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: uuid.UUID,
    data: TagUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Tag)
        .where(Tag.id == tag_id, Tag.user_id == user.id)
        .options(selectinload(Tag.subscriptions))
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    if data.name is not None:
        tag.name = data.name
    if data.color is not None:
        tag.color = data.color
    await db.commit()
    await db.refresh(tag)
    result = await db.execute(
        select(Tag).where(Tag.id == tag.id).options(selectinload(Tag.subscriptions))
    )
    tag = result.scalar_one()
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        subscription_count=len(tag.subscriptions),
    )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id, Tag.user_id == user.id)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    await db.delete(tag)
    await db.commit()
