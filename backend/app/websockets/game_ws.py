from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import json
from ..services.game_service import GameService
from ..services.redis_service import RedisService

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}  # game_id -> {player_id -> websocket}
        self.player_games: Dict[int, Set[int]] = {}  # player_id -> set of game_ids

    async def connect(self, websocket: WebSocket, game_id: int, player_id: int):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}
        self.active_connections[game_id][player_id] = websocket
        
        if player_id not in self.player_games:
            self.player_games[player_id] = set()
        self.player_games[player_id].add(game_id)

    def disconnect(self, game_id: int, player_id: int):
        if game_id in self.active_connections:
            self.active_connections[game_id].pop(player_id, None)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
        
        if player_id in self.player_games:
            self.player_games[player_id].remove(game_id)
            if not self.player_games[player_id]:
                del self.player_games[player_id]

    async def broadcast_to_game(self, game_id: int, message: dict):
        if game_id in self.active_connections:
            for websocket in self.active_connections[game_id].values():
                await websocket.send_json(message)

    async def send_personal_message(self, game_id: int, player_id: int, message: dict):
        if game_id in self.active_connections and player_id in self.active_connections[game_id]:
            await self.active_connections[game_id][player_id].send_json(message)

class GameWebSocket:
    def __init__(self, game_service: GameService, redis_service: RedisService):
        self.manager = ConnectionManager()
        self.game_service = game_service
        self.redis_service = redis_service

    async def handle_connection(self, websocket: WebSocket, game_id: int, player_id: int):
        await self.manager.connect(websocket, game_id, player_id)
        
        try:
            while True:
                data = await websocket.receive_json()
                await self.handle_message(game_id, player_id, data)
                
        except WebSocketDisconnect:
            self.manager.disconnect(game_id, player_id)
            await self.manager.broadcast_to_game(
                game_id,
                {
                    "type": "player_disconnected",
                    "player_id": player_id
                }
            )

    async def handle_message(self, game_id: int, player_id: int, data: dict):
        message_type = data.get("type")
        
        if message_type == "mark_number":
            number = data.get("number")
            card = self.redis_service.get_player_card(game_id, player_id)
            if card:
                # Обновляем отмеченные числа в карточке
                for row in range(3):
                    for col in range(9):
                        if card["numbers"][row][col] == number:
                            card["marked"][row][col] = True
                self.redis_service.set_player_card(game_id, player_id, card)
                
                await self.manager.send_personal_message(
                    game_id,
                    player_id,
                    {
                        "type": "card_updated",
                        "card": card
                    }
                )
                
        elif message_type == "claim_victory":
            success, error = self.game_service.check_victory(game_id, player_id)
            if success:
                self.game_service.end_game(game_id, player_id)
                await self.manager.broadcast_to_game(
                    game_id,
                    {
                        "type": "game_over",
                        "winner_id": player_id
                    }
                )
            else:
                await self.manager.send_personal_message(
                    game_id,
                    player_id,
                    {
                        "type": "error",
                        "message": error
                    }
                )
                
        elif message_type == "request_number":
            # Только создатель игры может запрашивать новые числа
            game_state = self.redis_service.get_game_state(game_id)
            if game_state and game_state["players"][0] == player_id:
                number, error = self.game_service.draw_number(game_id)
                if number:
                    await self.manager.broadcast_to_game(
                        game_id,
                        {
                            "type": "new_number",
                            "number": number
                        }
                    )
                else:
                    await self.manager.send_personal_message(
                        game_id,
                        player_id,
                        {
                            "type": "error",
                            "message": error
                        }
                    ) 