from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..core.achievements import achievement_manager, Achievement, AchievementProgress, AchievementType
from ..core.auth import get_current_user
from ..models.models import User

router = APIRouter()

@router.get("/", response_model=List[Achievement])
async def get_achievements(current_user: User = Depends(get_current_user)):
    """
    Получить все достижения пользователя.
    
    Returns:
        List[Achievement]: Список всех достижений с информацией о разблокировке
    """
    return await achievement_manager.get_user_achievements(str(current_user.id))

@router.get("/progress/{achievement_type}", response_model=AchievementProgress)
async def get_achievement_progress(
    achievement_type: AchievementType,
    current_user: User = Depends(get_current_user)
):
    """
    Получить прогресс конкретного достижения.
    
    Args:
        achievement_type (AchievementType): Тип достижения
        
    Returns:
        AchievementProgress: Информация о прогрессе достижения
    """
    progress = await achievement_manager.get_achievement_progress(
        str(current_user.id),
        achievement_type
    )
    if not progress:
        raise HTTPException(status_code=404, detail="Achievement progress not found")
    return progress

@router.get("/points", response_model=int)
async def get_achievement_points(current_user: User = Depends(get_current_user)):
    """
    Получить общее количество очков достижений пользователя.
    
    Returns:
        int: Количество очков достижений
    """
    achievements = await achievement_manager.get_user_achievements(str(current_user.id))
    return sum(
        achievement.points
        for achievement in achievements
        if achievement.unlocked_at is not None
    )

@router.get("/unlocked", response_model=List[Achievement])
async def get_unlocked_achievements(current_user: User = Depends(get_current_user)):
    """
    Получить список разблокированных достижений.
    
    Returns:
        List[Achievement]: Список разблокированных достижений
    """
    achievements = await achievement_manager.get_user_achievements(str(current_user.id))
    return [ach for ach in achievements if ach.unlocked_at is not None]

@router.get("/locked", response_model=List[Achievement])
async def get_locked_achievements(current_user: User = Depends(get_current_user)):
    """
    Получить список заблокированных достижений (кроме секретных).
    
    Returns:
        List[Achievement]: Список заблокированных достижений
    """
    achievements = await achievement_manager.get_user_achievements(str(current_user.id))
    return [
        ach for ach in achievements
        if ach.unlocked_at is None and not ach.secret
    ] 