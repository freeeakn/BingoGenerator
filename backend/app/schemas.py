from pydantic import BaseModel, EmailStr, conint
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    rating: int
    games_played: int
    games_won: int
    created_at: datetime

    class Config:
        from_attributes = True

class GameCard(BaseModel):
    numbers: List[List[int]]
    marked: List[List[bool]]

class GameCreate(BaseModel):
    max_players: conint(ge=2, le=4) = 4

class GameJoin(BaseModel):
    game_id: int

class GameState(BaseModel):
    id: int
    status: str
    current_number: Optional[int]
    called_numbers: List[int]
    players: List[User]
    creator: User
    max_players: int
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True

class GameAction(BaseModel):
    game_id: int
    action: str  # mark_number, claim_victory
    number: Optional[int]

class GameHistoryResponse(BaseModel):
    id: int
    game_id: int
    winner_id: int
    duration: int
    players_count: int
    created_at: datetime

    class Config:
        from_attributes = True 