from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import plugin_service

router = APIRouter(prefix="/plugins", tags=["plugins"])


class GitInstallRequest(BaseModel):
    url: str


@router.get("/")
async def list_plugins(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plugins = await plugin_service.list_plugins(db)
    return [
        {
            "name": p.name,
            "display_name": p.display_name,
            "version": p.version,
            "author": p.author,
            "description": p.description,
            "adapter_class": p.adapter_class,
            "enabled": p.enabled,
            "installed_at": p.installed_at,
        }
        for p in plugins
    ]


@router.post("/install/git", status_code=201)
async def install_from_git(
    body: GitInstallRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # WARNING: Plugin install executes arbitrary code. Restrict to first registered user (admin).
    from sqlalchemy import select as sa_select, func as sa_func
    min_result = await db.execute(sa_select(sa_func.min(User.created_at)))
    first_user_time = min_result.scalar()
    if user.created_at != first_user_time:
        raise HTTPException(status_code=403, detail="Only the admin user can install plugins")
    try:
        plugin = await plugin_service.install_from_git(db, body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "name": plugin.name,
        "display_name": plugin.display_name,
        "version": plugin.version,
        "enabled": plugin.enabled,
    }


@router.post("/install/zip", status_code=201)
async def install_from_zip(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select as sa_select, func as sa_func
    min_result = await db.execute(sa_select(sa_func.min(User.created_at)))
    first_user_time = min_result.scalar()
    if user.created_at != first_user_time:
        raise HTTPException(status_code=403, detail="Only the admin user can install plugins")
    max_size = 10 * 1024 * 1024  # 10 MB
    data = await file.read(max_size + 1)
    if len(data) > max_size:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
    try:
        plugin = await plugin_service.install_from_zip(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "name": plugin.name,
        "display_name": plugin.display_name,
        "version": plugin.version,
        "enabled": plugin.enabled,
    }


@router.delete("/{name}")
async def uninstall_plugin(
    name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await plugin_service.uninstall_plugin(db, name)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"detail": "Plugin uninstalled"}


@router.post("/{name}/enable")
async def enable_plugin(
    name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plugin = await plugin_service.toggle_plugin(db, name, enable=True)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"name": plugin.name, "enabled": plugin.enabled}


@router.post("/{name}/disable")
async def disable_plugin(
    name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plugin = await plugin_service.toggle_plugin(db, name, enable=False)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return {"name": plugin.name, "enabled": plugin.enabled}
