from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from enum import Enum

class ErrorCode(str, Enum):
    # Auth errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Game errors
    GAME_NOT_FOUND = "GAME_NOT_FOUND"
    GAME_ALREADY_STARTED = "GAME_ALREADY_STARTED"
    GAME_ALREADY_FINISHED = "GAME_ALREADY_FINISHED"
    INVALID_MOVE = "INVALID_MOVE"
    NOT_YOUR_TURN = "NOT_YOUR_TURN"
    
    # User errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    
    # WebSocket errors
    WS_CONNECTION_ERROR = "WS_CONNECTION_ERROR"
    WS_AUTHENTICATION_ERROR = "WS_AUTHENTICATION_ERROR"

class BingoException(HTTPException):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.details = details
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details
            }
        )

async def bingo_exception_handler(request: Request, exc: BingoException):
    """Global exception handler for BingoException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.detail["message"],
            "details": exc.details
        }
    )

# Example usage:
# raise BingoException(
#     code=ErrorCode.GAME_NOT_FOUND,
#     message="Game with specified ID not found",
#     status_code=404
# ) 