from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from typing import List
from ..models.models import User
from ..schemas import GameCreate, GameState, GameAction, GameHistoryResponse
from ..services.game_service import GameService
from ..services.redis_service import RedisService
from ..websockets.game_ws import GameWebSocket
from ..core.database import get_db
from .auth import get_current_user

router = APIRouter()

# Инициализация сервисов
redis_service = RedisService()
game_websocket = None

def get_game_service(db: Session = Depends(get_db)) -> GameService:
    return GameService(db, redis_service)

@router.post("/games", response_model=GameState)
async def create_game(
    game_data: GameCreate,
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service)
):
    """Создание новой игры"""
    game = game_service.create_game(current_user, game_data.max_players)
    return GameState.from_orm(game)

@router.get("/games/active", response_model=List[GameState])
async def list_active_games(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка активных игр"""
    games = db.query(Game).filter(Game.status == "waiting").all()
    return [GameState.from_orm(game) for game in games]

@router.post("/games/{game_id}/join")
async def join_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service)
):
    """Присоединение к игре"""
    success, error = game_service.join_game(game_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return {"message": "Successfully joined the game"}

@router.post("/games/{game_id}/start")
async def start_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service)
):
    """Начало игры"""
    success, error = game_service.start_game(game_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return {"message": "Game started"}

@router.get("/games/{game_id}", response_model=GameState)
async def get_game_state(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение состояния игры"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return GameState.from_orm(game)

@router.get("/games/history", response_model=List[GameHistoryResponse])
async def get_game_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение истории игр пользователя"""
    history = db.query(GameHistory).filter(
        (GameHistory.winner_id == current_user.id)
    ).order_by(GameHistory.created_at.desc()).all()
    return [GameHistoryResponse.from_orm(h) for h in history]

@router.websocket("/ws/game/{game_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    game_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint для игры"""
    try:
        # Проверка токена и получение пользователя
        user = await get_current_user(token, db)
        
        global game_websocket
        if game_websocket is None:
            game_websocket = GameWebSocket(
                game_service=GameService(db, redis_service),
                redis_service=redis_service
            )
        
        await game_websocket.handle_connection(websocket, game_id, user.id)
        
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION) 