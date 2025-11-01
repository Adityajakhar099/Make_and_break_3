from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()
# simple in-memory manager keyed by board id
class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, board_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(board_id, []).append(websocket)

    async def disconnect(self, board_id: str, websocket: WebSocket):
        conns = self.active.get(board_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, board_id: str, payload: dict):
        conns = self.active.get(board_id, [])
        for ws in conns.copy():
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect(board_id, ws)

manager = ConnectionManager()

@router.websocket("/{board_id}")
async def board_ws(websocket: WebSocket, board_id: str):
    await manager.connect(board_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast received message to other clients on same board
            await manager.broadcast(board_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(board_id, websocket)
