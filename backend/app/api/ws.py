import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.auth_service import decode_access_token
from app.services.notification_service import notify_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(...)):
    user_id_str = decode_access_token(token)
    if not user_id_str:
        await ws.close(code=4001, reason="Invalid token")
        return

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        await ws.close(code=4001, reason="Invalid token payload")
        return

    await notify_manager.connect(user_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        notify_manager.disconnect(user_id, ws)
