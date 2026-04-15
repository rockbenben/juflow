from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.opml_service import import_opml, export_opml
from app.services.subscription_service import list_subscriptions

router = APIRouter(prefix="/opml", tags=["opml"])

_MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB


@router.post("/import")
async def import_opml_endpoint(file: UploadFile = File(...), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await file.read(_MAX_UPLOAD_SIZE + 1)
    if len(content) > _MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 2 MB)")
    result = await import_opml(db, user.id, content)
    return result


@router.get("/export")
async def export_opml_endpoint(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    subs = await list_subscriptions(db, user.id)
    xml = export_opml(subs)
    return Response(content=xml, media_type="text/xml",
        headers={"Content-Disposition": 'attachment; filename="juflow-subscriptions.opml"'})
