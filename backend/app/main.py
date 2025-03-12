from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from .core.cache import CacheManager
from .core.logging import LogConfig
from .core.rate_limit import RateLimitManager
from .core.tasks import BackgroundTasks
from .core.events import event_manager
from .core.chat import chat_manager
from .core.notifications import notification_manager
from .core.achievements import AchievementManager
from .routes import auth, game, websockets, achievements
from .core.database import engine
from .models.models import Base
import uvicorn

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Инициализация менеджера достижений
achievement_manager = AchievementManager()

app = FastAPI(
    title="Bingo Game API",
    description="""
    Bingo Game API - Многопользовательская игра в Бинго с WebSocket поддержкой.
    
    ## Возможности
    
    - Аутентификация и авторизация пользователей
    - Создание и управление игровыми сессиями
    - Реалтайм игровой процесс через WebSocket
    - Чат между игроками
    - Система достижений и рейтингов
    - Уведомления о важных событиях
    
    ## Технические детали
    
    - JWT аутентификация
    - WebSocket для реалтайм коммуникации
    - Redis для кэширования и pub/sub
    - Prometheus мониторинг
    - Логирование через loguru
    - Sentry для отслеживания ошибок
    - Система достижений с прогрессом
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка мониторинга (перед добавлением middleware)
LogConfig.setup_monitoring(app)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(game.router, prefix="/game", tags=["game"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])
app.include_router(achievements.router, prefix="/achievements", tags=["achievements"])

# Startup events
@app.on_event("startup")
async def startup_event():
    # Initialize cache and Redis
    await CacheManager.init_cache()
    
    # Initialize rate limiter
    await RateLimitManager.init_limiter()
    
    # Setup logging and monitoring
    LogConfig.setup_logging()
    LogConfig.setup_sentry()
    
    # Start background tasks
    await BackgroundTasks.cleanup_inactive_games()
    await BackgroundTasks.update_player_ratings()
    await BackgroundTasks.generate_daily_statistics()

# Shutdown events
@app.on_event("shutdown")
async def shutdown_event():
    # Close Redis connections
    await CacheManager.close()

@app.get("/", tags=["root"])
async def root():
    """
    Корневой endpoint API.
    
    Returns:
        dict: Приветственное сообщение и ссылки на документацию
    """
    return {
        "message": "Welcome to Bingo Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Добавляем security схемы
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT токен авторизации. Получите через POST /api/auth/token"
        }
    }

    # Добавляем описание тегов
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "Операции аутентификации и управления пользователями"
        },
        {
            "name": "game",
            "description": "Управление игровыми сессиями и игровым процессом"
        },
        {
            "name": "websockets",
            "description": "WebSocket endpoints для реалтайм коммуникации"
        },
        {
            "name": "achievements",
            "description": """
            Система достижений и наград.
            
            ## Типы достижений
            - Игровые (завершение игр, победы)
            - Социальные (общение в чате, друзья)
            - Статистические (рейтинг, очки)
            - Специальные (уникальные события)
            
            ## Прогресс достижений
            Каждое достижение имеет:
            - Текущий прогресс
            - Целевое значение
            - Статус (заблокировано/разблокировано)
            - Дату получения
            - Награду в очках
            """
        }
    ]

    # Добавляем общие схемы компонентов
    openapi_schema["components"]["schemas"] = {
        "HTTPError": {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "description": "Описание ошибки"
                },
                "code": {
                    "type": "string",
                    "description": "Код ошибки"
                }
            },
            "required": ["detail"]
        },
        "GameState": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "ID игры"
                },
                "status": {
                    "type": "string",
                    "enum": ["waiting", "starting", "in_progress", "finished", "cancelled"],
                    "description": "Статус игры"
                },
                "players": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Список игроков"
                },
                "current_turn": {
                    "type": "string",
                    "description": "Имя игрока, чей сейчас ход"
                },
                "winner": {
                    "type": "string",
                    "nullable": True,
                    "description": "Имя победителя (если игра завершена)"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Время создания игры"
                },
                "updated_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Время последнего обновления"
                }
            }
        },
        "PlayerStats": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Имя игрока"
                },
                "games_played": {
                    "type": "integer",
                    "description": "Количество сыгранных игр"
                },
                "games_won": {
                    "type": "integer",
                    "description": "Количество побед"
                },
                "win_rate": {
                    "type": "number",
                    "format": "float",
                    "description": "Процент побед"
                },
                "rating": {
                    "type": "integer",
                    "description": "Рейтинг игрока"
                }
            }
        },
        "ChatMessage": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["message", "system"],
                    "description": "Тип сообщения"
                },
                "player": {
                    "type": "string",
                    "description": "Имя отправителя"
                },
                "text": {
                    "type": "string",
                    "description": "Текст сообщения"
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Время отправки"
                },
                "message_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Уникальный ID сообщения"
                }
            }
        },
        "Achievement": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "type": {"type": "string", "enum": ["GAME", "SOCIAL", "STATS", "SPECIAL"]},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "icon": {"type": "string"},
                "points": {"type": "integer"},
                "target_value": {"type": "integer"},
                "is_secret": {"type": "boolean"},
                "unlocked": {"type": "boolean"},
                "unlock_date": {"type": "string", "format": "date-time", "nullable": True}
            }
        },
        "AchievementProgress": {
            "type": "object",
            "properties": {
                "achievement_id": {"type": "string"},
                "current_value": {"type": "integer"},
                "target_value": {"type": "integer"},
                "percentage": {"type": "number", "format": "float"}
            }
        }
    }

    # Добавляем примеры ответов
    openapi_schema["components"]["examples"] = {
        "GameStateExample": {
            "value": {
                "id": 1,
                "status": "in_progress",
                "players": ["player1", "player2"],
                "current_turn": "player1",
                "winner": None,
                "created_at": "2024-03-20T15:30:00Z",
                "updated_at": "2024-03-20T15:35:00Z"
            }
        },
        "PlayerStatsExample": {
            "value": {
                "username": "player1",
                "games_played": 10,
                "games_won": 7,
                "win_rate": 70.0,
                "rating": 1500
            }
        },
        "ChatMessageExample": {
            "value": {
                "type": "message",
                "player": "player1",
                "text": "Привет всем!",
                "timestamp": "2024-03-20T15:30:00Z",
                "message_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        },
        "ErrorExample": {
            "value": {
                "detail": "Game not found",
                "code": "GAME_NOT_FOUND"
            }
        },
        "AchievementExample": {
            "value": {
                "id": "first_win",
                "type": "GAME",
                "title": "Первая победа",
                "description": "Выиграйте свою первую игру в Бинго",
                "icon": "🏆",
                "points": 100,
                "target_value": 1,
                "is_secret": False,
                "unlocked": True,
                "unlock_date": "2023-12-10T15:30:00Z"
            }
        },
        "AchievementProgressExample": {
            "value": {
                "achievement_id": "chat_master",
                "current_value": 75,
                "target_value": 100,
                "percentage": 75.0
            }
        }
    }

    # Добавляем общие параметры
    openapi_schema["components"]["parameters"] = {
        "GameIdParam": {
            "name": "game_id",
            "in": "path",
            "required": True,
            "schema": {
                "type": "integer",
                "description": "ID игры"
            }
        },
        "TokenParam": {
            "name": "token",
            "in": "query",
            "required": True,
            "schema": {
                "type": "string",
                "description": "JWT токен для WebSocket подключения"
            }
        }
    }

    # Добавляем общие ответы
    openapi_schema["components"]["responses"] = {
        "401": {
            "description": "Не авторизован",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/HTTPError"
                    },
                    "example": {
                        "detail": "Could not validate credentials"
                    }
                }
            }
        },
        "404": {
            "description": "Ресурс не найден",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/HTTPError"
                    },
                    "example": {
                        "detail": "Game not found"
                    }
                }
            }
        },
        "409": {
            "description": "Конфликт",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/HTTPError"
                    },
                    "example": {
                        "detail": "Game already started"
                    }
                }
            }
        }
    }
    
    # Применяем security ко всем endpoints кроме аутентификации
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if operation.get("tags") and "auth" not in operation["tags"]:
                operation["security"] = [{"bearerAuth": []}]
                # Добавляем общие ответы для всех защищенных endpoints
                if "responses" not in operation:
                    operation["responses"] = {}
                operation["responses"].update({
                    "401": {"$ref": "#/components/responses/401"},
                    "404": {"$ref": "#/components/responses/404"},
                    "409": {"$ref": "#/components/responses/409"}
                })
    
    openapi_schema["paths"]["/ws/game/{game_id}"] = {
        "get": {
            "tags": ["websockets"],
            "summary": "Game WebSocket",
            "description": """
            WebSocket соединение для игровой сессии.
            
            ## Входящие сообщения:
            - `{"type": "move", "data": {"number": int}}` - Ход игрока
            - `{"type": "ready"}` - Готовность к игре
            
            ## Исходящие сообщения:
            - `{"type": "game_state", "data": {...}}` - Состояние игры
            - `{"type": "move", "data": {"player": str, "number": int}}` - Ход игрока
            - `{"type": "winner", "data": {"player": str}}` - Победитель
            - `{"type": "player_disconnect", "player": str}` - Отключение игрока
            """,
            "parameters": [
                {"$ref": "#/components/parameters/GameIdParam"},
                {"$ref": "#/components/parameters/TokenParam"}
            ],
            "responses": {
                "101": {
                    "description": "WebSocket Protocol Handshake"
                },
                "4000": {
                    "description": "Ошибка подключения"
                },
                "4004": {
                    "description": "Игра не найдена"
                }
            }
        }
    }

    openapi_schema["paths"]["/ws/chat/{game_id}"] = {
        "get": {
            "tags": ["websockets"],
            "summary": "Chat WebSocket",
            "description": """
            WebSocket соединение для чата игры.
            
            ## Входящие сообщения:
            - `{"type": "message", "text": str}` - Сообщение в чат
            
            ## Исходящие сообщения:
            - `{"type": "message", "player": str, "text": str}` - Сообщение от игрока
            - `{"type": "system", "text": str}` - Системное сообщение
            """,
            "parameters": [
                {"$ref": "#/components/parameters/GameIdParam"},
                {"$ref": "#/components/parameters/TokenParam"}
            ],
            "responses": {
                "101": {
                    "description": "WebSocket Protocol Handshake"
                },
                "4000": {
                    "description": "Ошибка подключения"
                },
                "4004": {
                    "description": "Игра не найдена"
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log error
    LogConfig.log_error(exc, {"path": request.url.path})
    
    # Return error response
    return {
        "detail": "Internal server error",
        "code": "INTERNAL_ERROR"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 