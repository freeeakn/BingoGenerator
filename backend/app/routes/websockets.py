from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List, Dict
from ..core.database import get_db
from ..models.models import User, Game
from sqlalchemy.orm import Session
from ..routes.auth import get_current_user
import json

router = APIRouter()

# Хранилище активных соединений
class ConnectionManager:
    def __init__(self):
        # {game_id: {user_id: WebSocket}}
        self.game_connections: Dict[int, Dict[int, WebSocket]] = {}
        # {game_id: {user_id: WebSocket}}
        self.chat_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect_to_game(self, game_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.game_connections:
            self.game_connections[game_id] = {}
        self.game_connections[game_id][user_id] = websocket

    async def connect_to_chat(self, game_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.chat_connections:
            self.chat_connections[game_id] = {}
        self.chat_connections[game_id][user_id] = websocket

    async def disconnect_from_game(self, game_id: int, user_id: int):
        if game_id in self.game_connections:
            self.game_connections[game_id].pop(user_id, None)
            if not self.game_connections[game_id]:
                self.game_connections.pop(game_id)

    async def disconnect_from_chat(self, game_id: int, user_id: int):
        if game_id in self.chat_connections:
            self.chat_connections[game_id].pop(user_id, None)
            if not self.chat_connections[game_id]:
                self.chat_connections.pop(game_id)

    async def broadcast_game_message(self, game_id: int, message: dict):
        if game_id in self.game_connections:
            for connection in self.game_connections[game_id].values():
                await connection.send_json(message)

    async def broadcast_chat_message(self, game_id: int, message: dict):
        if game_id in self.chat_connections:
            for connection in self.chat_connections[game_id].values():
                await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/game/{game_id}")
async def game_websocket(
    websocket: WebSocket,
    game_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket соединение для игровой сессии.
    
    Args:
        websocket: WebSocket соединение
        game_id: ID игры
        token: JWT токен для аутентификации
        db: Сессия базы данных
    
    Messages:
        Входящие сообщения:
        - {"type": "move", "data": {"number": int}} - Ход игрока
        - {"type": "ready"} - Готовность к игре
        
        Исходящие сообщения:
        - {"type": "game_state", "data": {...}} - Состояние игры
        - {"type": "move", "data": {"player": str, "number": int}} - Ход игрока
        - {"type": "winner", "data": {"player": str}} - Победитель
    
    Raises:
        WebSocketDisconnect: При разрыве соединения
    """
    try:
        user = await get_current_user(token, db)
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            await websocket.close(code=4004, reason="Game not found")
            return
            
        await manager.connect_to_game(game_id, user.id, websocket)
        try:
            while True:
                data = await websocket.receive_json()
                # Обработка игровых событий
                await manager.broadcast_game_message(game_id, {
                    "type": data["type"],
                    "player": user.username,
                    "data": data.get("data", {})
                })
        except WebSocketDisconnect:
            await manager.disconnect_from_game(game_id, user.id)
            await manager.broadcast_game_message(game_id, {
                "type": "player_disconnect",
                "player": user.username
            })
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))

@router.websocket("/chat/{game_id}")
async def chat_websocket(
    websocket: WebSocket,
    game_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket соединение для чата игры.
    
    Args:
        websocket: WebSocket соединение
        game_id: ID игры
        token: JWT токен для аутентификации
        db: Сессия базы данных
    
    Messages:
        Входящие сообщения:
        - {"type": "message", "text": str} - Сообщение в чат
        
        Исходящие сообщения:
        - {"type": "message", "player": str, "text": str} - Сообщение от игрока
        - {"type": "system", "text": str} - Системное сообщение
    
    Raises:
        WebSocketDisconnect: При разрыве соединения
    """
    try:
        user = await get_current_user(token, db)
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            await websocket.close(code=4004, reason="Game not found")
            return
            
        await manager.connect_to_chat(game_id, user.id, websocket)
        await manager.broadcast_chat_message(game_id, {
            "type": "system",
            "text": f"{user.username} присоединился к чату"
        })
        
        try:
            while True:
                data = await websocket.receive_json()
                if data["type"] == "message":
                    await manager.broadcast_chat_message(game_id, {
                        "type": "message",
                        "player": user.username,
                        "text": data["text"]
                    })
        except WebSocketDisconnect:
            await manager.disconnect_from_chat(game_id, user.id)
            await manager.broadcast_chat_message(game_id, {
                "type": "system",
                "text": f"{user.username} покинул чат"
            })
    except Exception as e:
        await websocket.close(code=4000, reason=str(e)) 