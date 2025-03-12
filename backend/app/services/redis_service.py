import redis
import json
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class RedisService:
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv("REDIS_URL"))

    def set_game_state(self, game_id: int, state: Dict) -> None:
        """Сохранить состояние игры в Redis"""
        self.redis_client.setex(
            f"game:{game_id}",
            3600,  # TTL: 1 hour
            json.dumps(state)
        )

    def get_game_state(self, game_id: int) -> Optional[Dict]:
        """Получить состояние игры из Redis"""
        state = self.redis_client.get(f"game:{game_id}")
        return json.loads(state) if state else None

    def add_player_to_game(self, game_id: int, player_id: int) -> None:
        """Добавить игрока в игру"""
        self.redis_client.sadd(f"game:{game_id}:players", player_id)

    def remove_player_from_game(self, game_id: int, player_id: int) -> None:
        """Удалить игрока из игры"""
        self.redis_client.srem(f"game:{game_id}:players", player_id)

    def get_game_players(self, game_id: int) -> List[int]:
        """Получить список игроков в игре"""
        players = self.redis_client.smembers(f"game:{game_id}:players")
        return [int(player) for player in players]

    def set_player_card(self, game_id: int, player_id: int, card: Dict) -> None:
        """Сохранить карточку игрока"""
        self.redis_client.setex(
            f"game:{game_id}:player:{player_id}:card",
            3600,
            json.dumps(card)
        )

    def get_player_card(self, game_id: int, player_id: int) -> Optional[Dict]:
        """Получить карточку игрока"""
        card = self.redis_client.get(f"game:{game_id}:player:{player_id}:card")
        return json.loads(card) if card else None

    def add_called_number(self, game_id: int, number: int) -> None:
        """Добавить выпавшее число в список"""
        self.redis_client.rpush(f"game:{game_id}:called_numbers", number)

    def get_called_numbers(self, game_id: int) -> List[int]:
        """Получить список выпавших чисел"""
        numbers = self.redis_client.lrange(f"game:{game_id}:called_numbers", 0, -1)
        return [int(num) for num in numbers]

    def clear_game_data(self, game_id: int) -> None:
        """Очистить все данные игры"""
        keys = self.redis_client.keys(f"game:{game_id}*")
        if keys:
            self.redis_client.delete(*keys) 