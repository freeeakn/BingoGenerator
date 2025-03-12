import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..models.models import Game, User, GameHistory
from .redis_service import RedisService
from sqlalchemy.orm import Session

class GameService:
    def __init__(self, db: Session, redis: RedisService):
        self.db = db
        self.redis = redis

    def generate_card(self) -> List[List[int]]:
        """Генерация карточки для игры в лото"""
        # Создаем пустую карточку 3x9
        card = [[0 for _ in range(9)] for _ in range(3)]
        
        # Для каждой строки выбираем 5 случайных позиций
        for row in range(3):
            positions = random.sample(range(9), 5)
            
            # Заполняем выбранные позиции числами
            for col in positions:
                min_num = col * 10 + 1
                max_num = min_num + 9 if col < 8 else 91
                number = random.randint(min_num, max_num)
                
                # Проверяем, что число не повторяется в карточке
                while any(number in row for row in card):
                    number = random.randint(min_num, max_num)
                
                card[row][col] = number
        
        return card

    def create_game(self, creator: User, max_players: int) -> Game:
        """Создание новой игры"""
        game = Game(
            creator_id=creator.id,
            status="waiting",
            max_players=max_players,
            called_numbers=[]
        )
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        
        # Инициализация состояния игры в Redis
        self.redis.set_game_state(game.id, {
            "status": "waiting",
            "current_number": None,
            "called_numbers": [],
            "players": [creator.id]
        })
        
        return game

    def join_game(self, game_id: int, player: User) -> Tuple[bool, Optional[str]]:
        """Присоединение к игре"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return False, "Game not found"
        
        if game.status != "waiting":
            return False, "Game already started"
            
        current_players = self.redis.get_game_players(game_id)
        if len(current_players) >= game.max_players:
            return False, "Game is full"
            
        if player.id in current_players:
            return False, "Already in game"
        
        # Генерируем карточку для игрока
        card = self.generate_card()
        self.redis.set_player_card(game_id, player.id, {
            "numbers": card,
            "marked": [[False] * 9 for _ in range(3)]
        })
        
        self.redis.add_player_to_game(game_id, player.id)
        return True, None

    def start_game(self, game_id: int) -> Tuple[bool, Optional[str]]:
        """Начало игры"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return False, "Game not found"
            
        if game.status != "waiting":
            return False, "Game already started"
            
        players = self.redis.get_game_players(game_id)
        if len(players) < 2:
            return False, "Not enough players"
            
        game.status = "active"
        game.started_at = datetime.utcnow()
        self.db.commit()
        
        game_state = {
            "status": "active",
            "current_number": None,
            "called_numbers": [],
            "players": players
        }
        self.redis.set_game_state(game_id, game_state)
        
        return True, None

    def draw_number(self, game_id: int) -> Tuple[Optional[int], Optional[str]]:
        """Вытягивание следующего номера"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game or game.status != "active":
            return None, "Game not active"
            
        called_numbers = self.redis.get_called_numbers(game_id)
        available_numbers = list(set(range(1, 91)) - set(called_numbers))
        
        if not available_numbers:
            return None, "No more numbers"
            
        number = random.choice(available_numbers)
        self.redis.add_called_number(game_id, number)
        
        game_state = self.redis.get_game_state(game_id)
        game_state["current_number"] = number
        game_state["called_numbers"] = called_numbers + [number]
        self.redis.set_game_state(game_id, game_state)
        
        return number, None

    def check_victory(self, game_id: int, player_id: int) -> Tuple[bool, Optional[str]]:
        """Проверка победы игрока"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game or game.status != "active":
            return False, "Game not active"
            
        card = self.redis.get_player_card(game_id, player_id)
        if not card:
            return False, "Player card not found"
            
        called_numbers = set(self.redis.get_called_numbers(game_id))
        
        # Проверяем все числа в карточке
        for row in range(3):
            for col in range(9):
                if card["numbers"][row][col] != 0 and not card["marked"][row][col]:
                    if card["numbers"][row][col] not in called_numbers:
                        return False, "Invalid victory claim"
        
        return True, None

    def end_game(self, game_id: int, winner_id: int) -> None:
        """Завершение игры"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return
            
        game.status = "finished"
        game.finished_at = datetime.utcnow()
        
        # Обновляем статистику победителя
        winner = self.db.query(User).filter(User.id == winner_id).first()
        if winner:
            winner.games_won += 1
            winner.rating += 25  # Простая система рейтинга
            
        # Обновляем статистику всех игроков
        players = self.redis.get_game_players(game_id)
        for player_id in players:
            player = self.db.query(User).filter(User.id == player_id).first()
            if player:
                player.games_played += 1
                if player.id != winner_id:
                    player.rating = max(1000, player.rating - 10)
                    
        # Создаем запись в истории игр
        history = GameHistory(
            game_id=game_id,
            winner_id=winner_id,
            duration=(game.finished_at - game.started_at).seconds,
            players_count=len(players)
        )
        
        self.db.add(history)
        self.db.commit()
        
        # Очищаем данные игры из Redis
        self.redis.clear_game_data(game_id) 