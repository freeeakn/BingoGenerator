from fastapi_utils.tasks import repeat_every
from datetime import datetime, timedelta
from typing import List
from .logging import logger
from .cache import CacheManager

class BackgroundTasks:
    @staticmethod
    @repeat_every(seconds=60)
    async def cleanup_inactive_games():
        """Cleanup inactive games every minute"""
        try:
            redis = await CacheManager.get_redis()
            
            # Get all active games
            active_games = await redis.smembers("active_games")
            
            for game_id in active_games:
                # Check last activity
                last_activity = await redis.get(f"game:{game_id}:last_activity")
                if last_activity:
                    last_activity_time = datetime.fromisoformat(last_activity)
                    
                    # If inactive for more than 30 minutes
                    if datetime.now() - last_activity_time > timedelta(minutes=30):
                        await redis.srem("active_games", game_id)
                        logger.info(f"Cleaned up inactive game {game_id}")
                        
        except Exception as e:
            logger.error(f"Error in cleanup_inactive_games: {str(e)}")

    @staticmethod
    @repeat_every(seconds=300)
    async def update_player_ratings():
        """Update player ratings every 5 minutes"""
        try:
            redis = await CacheManager.get_redis()
            
            # Get all players that need rating update
            players_to_update = await redis.smembers("players_rating_update")
            
            for player_id in players_to_update:
                # Calculate new rating based on recent games
                new_rating = await calculate_player_rating(player_id)
                
                # Update rating in database
                await update_player_rating_in_db(player_id, new_rating)
                
                # Remove from update set
                await redis.srem("players_rating_update", player_id)
                
        except Exception as e:
            logger.error(f"Error in update_player_ratings: {str(e)}")

    @staticmethod
    @repeat_every(seconds=3600)
    async def generate_daily_statistics():
        """Generate daily statistics every hour"""
        try:
            # Calculate various statistics
            stats = {
                "total_games": await get_total_games_today(),
                "active_players": await get_active_players_count(),
                "average_game_duration": await calculate_average_game_duration(),
                "most_active_hours": await get_most_active_hours()
            }
            
            # Store statistics in Redis
            redis = await CacheManager.get_redis()
            # Convert all values to strings for Redis storage
            stats_str = {k: str(v) for k, v in stats.items()}
            await redis.hmset("daily_statistics", stats_str)
            
        except Exception as e:
            logger.error(f"Error in generate_daily_statistics: {str(e)}")

# Helper functions with default implementations
async def calculate_player_rating(player_id: str) -> int:
    # Default implementation returns base rating
    return 1000

async def update_player_rating_in_db(player_id: str, rating: int):
    # TODO: Implement database update
    pass

async def get_total_games_today() -> int:
    # Default implementation returns 0
    return 0

async def get_active_players_count() -> int:
    # Default implementation returns 0
    return 0

async def calculate_average_game_duration() -> float:
    # Default implementation returns 0.0
    return 0.0

async def get_most_active_hours() -> List[int]:
    # Default implementation returns empty list
    return [] 