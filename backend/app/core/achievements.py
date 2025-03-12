from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from .cache import CacheManager
from .logging import logger
from .notifications import notification_manager, NotificationType, NotificationPriority
from .events import event_manager, GameEventType, GameEvent

class AchievementType(str, Enum):
    # Игровые достижения
    FIRST_WIN = "first_win"                    # Первая победа
    WINNING_STREAK_3 = "winning_streak_3"      # 3 победы подряд
    WINNING_STREAK_5 = "winning_streak_5"      # 5 побед подряд
    FAST_WIN = "fast_win"                      # Победа менее чем за 2 минуты
    PERFECT_GAME = "perfect_game"              # Победа без ошибок
    
    # Социальные достижения
    SOCIAL_BUTTERFLY = "social_butterfly"       # 100 сообщений в чате
    POPULAR_PLAYER = "popular_player"          # 50 реакций на сообщения
    FRIEND_MAKER = "friend_maker"              # 10 друзей
    
    # Статистические достижения
    VETERAN = "veteran"                        # 100 игр
    MASTER = "master"                          # 50 побед
    HIGH_ROLLER = "high_roller"                # Рейтинг 2000+
    
    # Специальные достижения
    EARLY_BIRD = "early_bird"                  # Один из первых 100 игроков
    COMEBACK_KID = "comeback_kid"              # Победа после отставания в 10+ чисел
    LUCKY_NUMBER = "lucky_number"              # Выиграть с любимым числом

class Achievement(BaseModel):
    type: AchievementType
    title: str
    description: str
    icon: str
    points: int
    secret: bool = False
    progress_max: Optional[int] = None
    unlocked_at: Optional[datetime] = None
    current_progress: Optional[int] = None

class AchievementProgress(BaseModel):
    achievement_type: AchievementType
    current_value: int
    target_value: int
    last_updated: datetime = datetime.now()

class AchievementManager:
    # Определение достижений
    ACHIEVEMENTS = {
        AchievementType.FIRST_WIN: {
            "title": "Первая победа",
            "description": "Выиграйте свою первую игру",
            "icon": "🏆",
            "points": 10,
            "secret": False
        },
        AchievementType.WINNING_STREAK_3: {
            "title": "Победная серия",
            "description": "Выиграйте 3 игры подряд",
            "icon": "🔥",
            "points": 20,
            "secret": False
        },
        AchievementType.WINNING_STREAK_5: {
            "title": "Непобедимый",
            "description": "Выиграйте 5 игр подряд",
            "icon": "⚡",
            "points": 50,
            "secret": False
        },
        AchievementType.FAST_WIN: {
            "title": "Молниеносная победа",
            "description": "Выиграйте игру менее чем за 2 минуты",
            "icon": "⚡",
            "points": 30,
            "secret": False
        },
        AchievementType.PERFECT_GAME: {
            "title": "Безупречная игра",
            "description": "Выиграйте игру без единой ошибки",
            "icon": "💯",
            "points": 40,
            "secret": False
        },
        AchievementType.SOCIAL_BUTTERFLY: {
            "title": "Общительный игрок",
            "description": "Отправьте 100 сообщений в чат",
            "icon": "🦋",
            "points": 15,
            "progress_max": 100,
            "secret": False
        },
        AchievementType.POPULAR_PLAYER: {
            "title": "Популярный игрок",
            "description": "Получите 50 реакций на свои сообщения",
            "icon": "⭐",
            "points": 25,
            "progress_max": 50,
            "secret": False
        },
        AchievementType.FRIEND_MAKER: {
            "title": "Дружелюбный",
            "description": "Добавьте 10 друзей",
            "icon": "🤝",
            "points": 20,
            "progress_max": 10,
            "secret": False
        },
        AchievementType.VETERAN: {
            "title": "Ветеран",
            "description": "Сыграйте 100 игр",
            "icon": "👑",
            "points": 30,
            "progress_max": 100,
            "secret": False
        },
        AchievementType.MASTER: {
            "title": "Мастер",
            "description": "Выиграйте 50 игр",
            "icon": "🎯",
            "points": 50,
            "progress_max": 50,
            "secret": False
        },
        AchievementType.HIGH_ROLLER: {
            "title": "Высший рейтинг",
            "description": "Достигните рейтинга 2000+",
            "icon": "🌟",
            "points": 100,
            "progress_max": 2000,
            "secret": False
        },
        AchievementType.EARLY_BIRD: {
            "title": "Ранняя пташка",
            "description": "Один из первых 100 игроков",
            "icon": "🐦",
            "points": 50,
            "secret": True
        },
        AchievementType.COMEBACK_KID: {
            "title": "Король камбэков",
            "description": "Выиграйте после отставания в 10+ чисел",
            "icon": "🔄",
            "points": 40,
            "secret": True
        },
        AchievementType.LUCKY_NUMBER: {
            "title": "Счастливое число",
            "description": "Выиграйте с вашим любимым числом",
            "icon": "🍀",
            "points": 15,
            "secret": True
        }
    }

    def __init__(self):
        # Подписываемся на игровые события
        event_manager.subscribe(GameEventType.GAME_FINISHED, self._handle_game_finished)
        event_manager.subscribe(GameEventType.CHAT_MESSAGE, self._handle_chat_message)
        event_manager.subscribe(GameEventType.NUMBER_MARKED, self._handle_number_marked)

    async def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Получить все достижения пользователя"""
        try:
            redis = await CacheManager.get_redis()
            achievements_data = await redis.hgetall(f"user:{user_id}:achievements")
            
            achievements = []
            for ach_type in AchievementType:
                achievement = self.ACHIEVEMENTS[ach_type].copy()
                achievement["type"] = ach_type
                
                if ach_type.value in achievements_data:
                    data = achievements_data[ach_type.value]
                    achievement["unlocked_at"] = datetime.fromisoformat(data)
                
                achievements.append(Achievement(**achievement))
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {str(e)}")
            return []

    async def get_achievement_progress(
        self,
        user_id: str,
        achievement_type: AchievementType
    ) -> Optional[AchievementProgress]:
        """Получить прогресс достижения"""
        try:
            redis = await CacheManager.get_redis()
            progress_key = f"user:{user_id}:achievement_progress:{achievement_type.value}"
            progress_data = await redis.get(progress_key)
            
            if progress_data:
                return AchievementProgress(**progress_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting achievement progress: {str(e)}")
            return None

    async def unlock_achievement(
        self,
        user_id: str,
        achievement_type: AchievementType
    ):
        """Разблокировать достижение"""
        try:
            redis = await CacheManager.get_redis()
            achievement_key = f"user:{user_id}:achievements"
            
            # Проверяем, не получено ли уже достижение
            if await redis.hexists(achievement_key, achievement_type.value):
                return
            
            # Разблокируем достижение
            now = datetime.now()
            await redis.hset(
                achievement_key,
                achievement_type.value,
                now.isoformat()
            )
            
            # Добавляем очки
            points = self.ACHIEVEMENTS[achievement_type]["points"]
            await redis.hincrby(f"user:{user_id}:stats", "achievement_points", points)
            
            # Отправляем уведомление
            achievement = self.ACHIEVEMENTS[achievement_type]
            await notification_manager.send_notification(
                user_id=user_id,
                type=NotificationType.ACHIEVEMENT_UNLOCKED,
                title=f"Новое достижение: {achievement['title']}",
                message=f"Вы получили достижение '{achievement['title']}' {achievement['icon']}\n{achievement['description']}",
                priority=NotificationPriority.MEDIUM,
                data={
                    "achievement_type": achievement_type.value,
                    "points": points
                }
            )
            
        except Exception as e:
            logger.error(f"Error unlocking achievement: {str(e)}")

    async def update_progress(
        self,
        user_id: str,
        achievement_type: AchievementType,
        value: int
    ):
        """Обновить прогресс достижения"""
        try:
            if achievement_type not in self.ACHIEVEMENTS:
                return
                
            achievement = self.ACHIEVEMENTS[achievement_type]
            if "progress_max" not in achievement:
                return
                
            redis = await CacheManager.get_redis()
            progress_key = f"user:{user_id}:achievement_progress:{achievement_type.value}"
            
            # Обновляем прогресс
            progress = AchievementProgress(
                achievement_type=achievement_type,
                current_value=value,
                target_value=achievement["progress_max"]
            )
            await redis.set(progress_key, progress.json())
            
            # Если достигнут максимум, разблокируем достижение
            if value >= achievement["progress_max"]:
                await self.unlock_achievement(user_id, achievement_type)
                
        except Exception as e:
            logger.error(f"Error updating achievement progress: {str(e)}")

    async def _handle_game_finished(self, event: GameEvent):
        """Обработчик завершения игры"""
        try:
            winner_id = event.data.get("winner_id")
            if not winner_id:
                return
                
            # Проверяем первую победу
            await self._check_first_win(winner_id)
            
            # Проверяем победную серию
            await self._check_winning_streak(winner_id)
            
            # Проверяем быструю победу
            game_duration = event.data.get("duration")
            if game_duration and game_duration < 120:  # менее 2 минут
                await self.unlock_achievement(winner_id, AchievementType.FAST_WIN)
                
            # Проверяем безупречную игру
            errors = event.data.get("errors", 0)
            if errors == 0:
                await self.unlock_achievement(winner_id, AchievementType.PERFECT_GAME)
                
            # Обновляем статистику игр
            await self._update_games_stats(winner_id)
            
        except Exception as e:
            logger.error(f"Error handling game finished event: {str(e)}")

    async def _handle_chat_message(self, event: GameEvent):
        """Обработчик сообщений чата"""
        try:
            user_id = event.player_id
            if not user_id:
                return
                
            # Обновляем количество сообщений
            redis = await CacheManager.get_redis()
            messages_count = await redis.hincrby(
                f"user:{user_id}:stats",
                "chat_messages",
                1
            )
            
            # Проверяем достижение общительности
            await self.update_progress(
                user_id,
                AchievementType.SOCIAL_BUTTERFLY,
                messages_count
            )
            
        except Exception as e:
            logger.error(f"Error handling chat message event: {str(e)}")

    async def _handle_number_marked(self, event: GameEvent):
        """Обработчик отмеченных чисел"""
        try:
            user_id = event.player_id
            if not user_id:
                return
                
            # Проверяем камбэк
            game_state = event.data.get("game_state", {})
            player_numbers = len(game_state.get("marked_numbers", {}).get(user_id, []))
            leader_numbers = max(
                len(numbers)
                for player, numbers in game_state.get("marked_numbers", {}).items()
                if player != user_id
            )
            
            if leader_numbers - player_numbers >= 10:
                await self.unlock_achievement(user_id, AchievementType.COMEBACK_KID)
                
        except Exception as e:
            logger.error(f"Error handling number marked event: {str(e)}")

    async def _check_first_win(self, user_id: str):
        """Проверка первой победы"""
        try:
            redis = await CacheManager.get_redis()
            wins = await redis.hget(f"user:{user_id}:stats", "wins")
            
            if wins == "1":  # Первая победа
                await self.unlock_achievement(user_id, AchievementType.FIRST_WIN)
                
        except Exception as e:
            logger.error(f"Error checking first win: {str(e)}")

    async def _check_winning_streak(self, user_id: str):
        """Проверка победной серии"""
        try:
            redis = await CacheManager.get_redis()
            streak_key = f"user:{user_id}:winning_streak"
            
            # Увеличиваем серию побед
            streak = await redis.incr(streak_key)
            
            # Проверяем достижения
            if streak >= 3:
                await self.unlock_achievement(user_id, AchievementType.WINNING_STREAK_3)
            if streak >= 5:
                await self.unlock_achievement(user_id, AchievementType.WINNING_STREAK_5)
                
        except Exception as e:
            logger.error(f"Error checking winning streak: {str(e)}")

    async def _update_games_stats(self, user_id: str):
        """Обновление игровой статистики"""
        try:
            redis = await CacheManager.get_redis()
            
            # Обновляем количество игр
            games = await redis.hincrby(f"user:{user_id}:stats", "games_played", 1)
            await self.update_progress(user_id, AchievementType.VETERAN, games)
            
            # Обновляем количество побед
            wins = await redis.hincrby(f"user:{user_id}:stats", "wins", 1)
            await self.update_progress(user_id, AchievementType.MASTER, wins)
            
            # Проверяем рейтинг
            rating = int(await redis.hget(f"user:{user_id}:stats", "rating") or 0)
            await self.update_progress(user_id, AchievementType.HIGH_ROLLER, rating)
            
        except Exception as e:
            logger.error(f"Error updating games stats: {str(e)}")

# Создаем глобальный экземпляр менеджера достижений
achievement_manager = AchievementManager() 