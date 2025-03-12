from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
from .cache import CacheManager
from .logging import logger
import json
import aiosmtplib
from email.message import EmailMessage

class NotificationType(str, Enum):
    GAME_INVITATION = "game_invitation"
    GAME_STARTED = "game_started"
    TURN_NOTIFICATION = "turn_notification"
    GAME_FINISHED = "game_finished"
    CHAT_MENTION = "chat_mention"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    FRIEND_REQUEST = "friend_request"
    SYSTEM_NOTIFICATION = "system_notification"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class Notification(BaseModel):
    id: str
    type: NotificationType
    user_id: str
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    status: NotificationStatus = NotificationStatus.PENDING
    timestamp: datetime = datetime.now()
    data: Optional[Dict[str, Any]] = None
    read_at: Optional[datetime] = None

class NotificationManager:
    def __init__(self):
        self.email_config = {
            "hostname": "smtp.example.com",
            "port": 587,
            "username": "your-username",
            "password": "your-password"
        }

    async def send_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Send a notification to a user"""
        try:
            notification = Notification(
                id=f"notif_{datetime.now().timestamp()}",
                type=type,
                user_id=user_id,
                title=title,
                message=message,
                priority=priority,
                data=data
            )
            
            # Store in Redis
            redis = await CacheManager.get_redis()
            await redis.lpush(
                f"user:{user_id}:notifications",
                notification.json()
            )
            
            # Send real-time notification if user is online
            if await self._is_user_online(user_id):
                await self._send_websocket_notification(user_id, notification)
            
            # Send email for high priority notifications
            if priority == NotificationPriority.HIGH:
                await self._send_email_notification(user_id, notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise

    async def get_notifications(
        self,
        user_id: str,
        limit: int = 50,
        status: Optional[NotificationStatus] = None
    ) -> List[Notification]:
        """Get user's notifications"""
        try:
            redis = await CacheManager.get_redis()
            notifications = await redis.lrange(
                f"user:{user_id}:notifications",
                0,
                limit - 1
            )
            
            result = []
            for notif in notifications:
                notification = Notification(**json.loads(notif))
                if status and notification.status != status:
                    continue
                result.append(notification)
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return []

    async def mark_as_read(self, user_id: str, notification_id: str):
        """Mark notification as read"""
        try:
            redis = await CacheManager.get_redis()
            key = f"user:{user_id}:notifications"
            
            # Get notification
            notifications = await redis.lrange(key, 0, -1)
            for i, notif in enumerate(notifications):
                notification = Notification(**json.loads(notif))
                if notification.id == notification_id:
                    notification.status = NotificationStatus.READ
                    notification.read_at = datetime.now()
                    await redis.lset(key, i, notification.json())
                    break
                    
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")

    async def _is_user_online(self, user_id: str) -> bool:
        """Check if user is online"""
        redis = await CacheManager.get_redis()
        return await redis.exists(f"user:{user_id}:websocket")

    async def _send_websocket_notification(
        self,
        user_id: str,
        notification: Notification
    ):
        """Send notification via WebSocket"""
        try:
            redis = await CacheManager.get_redis()
            ws_connection = await redis.get(f"user:{user_id}:websocket")
            if ws_connection:
                # Send to WebSocket connection
                pass
                
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {str(e)}")

    async def _send_email_notification(
        self,
        user_id: str,
        notification: Notification
    ):
        """Send notification via email"""
        try:
            # Get user email
            user_email = await self._get_user_email(user_id)
            if not user_email:
                return
                
            # Create email message
            message = EmailMessage()
            message["From"] = "noreply@bingogame.com"
            message["To"] = user_email
            message["Subject"] = notification.title
            message.set_content(notification.message)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.email_config["hostname"],
                port=self.email_config["port"],
                username=self.email_config["username"],
                password=self.email_config["password"],
                use_tls=True
            )
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")

    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user's email address"""
        # Implementation depends on your user management system
        pass

# Create global notification manager instance
notification_manager = NotificationManager() 