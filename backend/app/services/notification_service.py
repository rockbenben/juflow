import json
import uuid
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[uuid.UUID, list[WebSocket]] = {}

    async def connect(self, user_id: uuid.UUID, ws: WebSocket):
        await ws.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(ws)

    def disconnect(self, user_id: uuid.UUID, ws: WebSocket):
        if user_id in self._connections:
            self._connections[user_id] = [c for c in self._connections[user_id] if c is not ws]
            if not self._connections[user_id]:
                del self._connections[user_id]

    async def notify_user(self, user_id: uuid.UUID, data: dict):
        if user_id not in self._connections:
            return
        message = json.dumps(data, default=str)
        dead = []
        for ws in self._connections[user_id]:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)


notify_manager = ConnectionManager()
