from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

# Связующая таблица для отношения many-to-many между игроками и играми
game_players = Table('game_players',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('game_id', Integer, ForeignKey('games.id')),
    Column('card', JSON),  # Карточка игрока
    Column('status', String)  # Статус игрока в игре (active, winner, etc.)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    rating = Column(Integer, default=1000)
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    games = relationship("Game", secondary=game_players, back_populates="players")
    created_games = relationship("Game", back_populates="creator")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)  # waiting, active, finished
    current_number = Column(Integer, nullable=True)
    called_numbers = Column(JSON, default=list)
    max_players = Column(Integer, default=4)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    
    # Отношения
    creator = relationship("User", back_populates="created_games")
    players = relationship("User", secondary=game_players, back_populates="games")

class GameHistory(Base):
    __tablename__ = "game_history"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    winner_id = Column(Integer, ForeignKey("users.id"))
    duration = Column(Integer)  # в секундах
    players_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow) 