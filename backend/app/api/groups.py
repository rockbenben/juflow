import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    max_result = await db.execute(
        select(func.max(Group.sort_order)).where(Group.user_id == user.id)
    )
    max_order = max_result.scalar() or 0
    group = Group(
        user_id=user.id,
        name=data.name,
        icon=data.icon,
        sort_order=max_order + 1,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.subscriptions))
    )
    group = result.scalar_one()
    return GroupResponse(
        id=group.id,
        name=group.name,
        icon=group.icon,
        sort_order=group.sort_order,
        subscription_count=len(group.subscriptions),
    )


@router.get("/", response_model=list[GroupResponse])
async def list_groups(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group)
        .where(Group.user_id == user.id)
        .options(selectinload(Group.subscriptions))
        .order_by(Group.sort_order.asc())
    )
    groups = result.scalars().all()
    return [
        GroupResponse(
            id=g.id,
            name=g.name,
            icon=g.icon,
            sort_order=g.sort_order,
            subscription_count=len(g.subscriptions),
        )
        for g in groups
    ]


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: uuid.UUID,
    data: GroupUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group)
        .where(Group.id == group_id, Group.user_id == user.id)
        .options(selectinload(Group.subscriptions))
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    if data.name is not None:
        group.name = data.name
    if data.icon is not None:
        group.icon = data.icon
    if data.sort_order is not None:
        group.sort_order = data.sort_order
    await db.commit()
    await db.refresh(group)
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.subscriptions))
    )
    group = result.scalar_one()
    return GroupResponse(
        id=group.id,
        name=group.name,
        icon=group.icon,
        sort_order=group.sort_order,
        subscription_count=len(group.subscriptions),
    )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group).where(Group.id == group_id, Group.user_id == user.id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    await db.delete(group)
    await db.commit()
