from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from .cache import CacheManager
from .logging import logger

class GameEventType(str, Enum):
    # Game lifecycle events
    GAME_CREATED = "game_created"
    GAME_STARTED = "game_started"
    GAME_FINISHED = "game_finished"
    GAME_CANCELLED = "game_cancelled"
    
    # Player events
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    PLAYER_READY = "player_ready"
    
    # Game actions
    NUMBER_CALLED = "number_called"
    NUMBER_MARKED = "number_marked"
    LINE_COMPLETED = "line_completed"
    BINGO_CALLED = "bingo_called"
    BINGO_VERIFIED = "bingo_verified"
    
    # Chat events
    CHAT_MESSAGE = "chat_message"
    CHAT_MODERATED = "chat_moderated"

class GameEvent(BaseModel):
    event_type: GameEventType
    game_id: str
    player_id: Optional[str]
    timestamp: datetime = datetime.now()
    data: Dict[str, Any]

class EventManager:
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        
    async def publish_event(self, event: GameEvent):
        """Publish game event to Redis and notify subscribers"""
        try:
            redis = await CacheManager.get_redis()
            
            # Store event in Redis
            event_data = event.dict()
            await redis.lpush(f"game:{event.game_id}:events", event_data)
            
            # Notify subscribers
            channel = f"game:{event.game_id}"
            await redis.publish(channel, event_data)
            
            # Log event
            logger.info(f"Game event published: {event.event_type} for game {event.game_id}")
            
            # Notify local subscribers
            if event.event_type in self.subscribers:
                for callback in self.subscribers[event.event_type]:
                    await callback(event)
                    
        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}")

    def subscribe(self, event_type: GameEventType, callback: callable):
        """Subscribe to specific event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def get_game_events(self, game_id: str, limit: int = 50) -> List[GameEvent]:
        """Get recent events for a game"""
        try:
            redis = await CacheManager.get_redis()
            events = await redis.lrange(f"game:{game_id}:events", 0, limit - 1)
            return [GameEvent(**event) for event in events]
        except Exception as e:
            logger.error(f"Error getting game events: {str(e)}")
            return []

# Create global event manager instance
event_manager = EventManager()

# Example usage:
# @event_manager.subscribe(GameEventType.PLAYER_JOINED)
# async def handle_player_joined(event: GameEvent):
#     # Handle player joined event
#     pass

# await event_manager.publish_event(GameEvent(
#     event_type=GameEventType.PLAYER_JOINED,
#     game_id="123",
#     player_id="456",
#     data={"username": "player1"}
# )) 