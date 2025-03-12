from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel
from .cache import CacheManager
from .logging import logger
from .events import event_manager, GameEvent, GameEventType
import json
import re

class ChatMessage(BaseModel):
    message_id: str
    game_id: str
    player_id: str
    content: str
    timestamp: datetime = datetime.now()
    type: str = "message"  # message, system, moderated
    status: str = "sent"  # sent, delivered, read
    mentions: List[str] = []
    reactions: Dict[str, List[str]] = {}  # emoji: [player_ids]

class ChatManager:
    def __init__(self):
        self.bad_words_pattern = re.compile(r'\b(bad|words|here)\b', re.IGNORECASE)
        
    async def send_message(self, message: ChatMessage):
        """Send a chat message"""
        try:
            # Moderate content
            moderated_content = await self.moderate_message(message.content)
            if moderated_content != message.content:
                message.type = "moderated"
                message.content = moderated_content
            
            # Extract mentions
            message.mentions = self._extract_mentions(message.content)
            
            # Store in Redis
            redis = await CacheManager.get_redis()
            await redis.lpush(
                f"game:{message.game_id}:chat",
                message.json()
            )
            
            # Publish event
            await event_manager.publish_event(GameEvent(
                event_type=GameEventType.CHAT_MESSAGE,
                game_id=message.game_id,
                player_id=message.player_id,
                data=message.dict()
            ))
            
            # Handle mentions notifications
            await self._handle_mentions(message)
            
            return message
            
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
            raise

    async def get_messages(
        self,
        game_id: str,
        limit: int = 50,
        before_timestamp: Optional[datetime] = None
    ) -> List[ChatMessage]:
        """Get chat messages for a game"""
        try:
            redis = await CacheManager.get_redis()
            messages = await redis.lrange(
                f"game:{game_id}:chat",
                0,
                limit - 1
            )
            
            result = []
            for msg in messages:
                message = ChatMessage(**json.loads(msg))
                if before_timestamp and message.timestamp >= before_timestamp:
                    continue
                result.append(message)
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            return []

    async def add_reaction(
        self,
        game_id: str,
        message_id: str,
        player_id: str,
        emoji: str
    ):
        """Add reaction to a message"""
        try:
            redis = await CacheManager.get_redis()
            message_key = f"game:{game_id}:chat:message:{message_id}"
            
            # Get message
            message_data = await redis.get(message_key)
            if not message_data:
                return
                
            message = ChatMessage(**json.loads(message_data))
            
            # Add reaction
            if emoji not in message.reactions:
                message.reactions[emoji] = []
            if player_id not in message.reactions[emoji]:
                message.reactions[emoji].append(player_id)
                
            # Save updated message
            await redis.set(message_key, message.json())
            
        except Exception as e:
            logger.error(f"Error adding reaction: {str(e)}")

    async def moderate_message(self, content: str) -> str:
        """Moderate message content"""
        # Replace bad words with asterisks
        return self.bad_words_pattern.sub(lambda m: '*' * len(m.group()), content)

    def _extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from message"""
        mentions = re.findall(r'@(\w+)', content)
        return list(set(mentions))

    async def _handle_mentions(self, message: ChatMessage):
        """Handle notifications for mentioned users"""
        for mentioned_user in message.mentions:
            # Add notification
            redis = await CacheManager.get_redis()
            notification = {
                "type": "mention",
                "game_id": message.game_id,
                "message_id": message.message_id,
                "from_user": message.player_id,
                "timestamp": message.timestamp.isoformat()
            }
            await redis.lpush(
                f"user:{mentioned_user}:notifications",
                json.dumps(notification)
            )

# Create global chat manager instance
chat_manager = ChatManager() 