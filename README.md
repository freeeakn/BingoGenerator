# Онлайн Лото: Мультиплеер

Этот проект представляет собой полноценную онлайн-версию игры в лото с поддержкой множества игроков. Программа позволяет играть в лото через интернет в режиме реального времени.

## Особенности

- Мультиплеер через WebSocket соединение
- Случайное выпадение бочонков
- Озвучивание номеров на русском языке
- Отображение оставшихся бочонков
- Система комнат для одновременных игр
- Сохранение состояния игры
- Аутентификация пользователей
- Рейтинговая система
- Чат между игроками

## Технический стек

### Backend
- FastAPI (асинхронный веб-фреймворк)
- PostgreSQL (база данных)
- Redis (кэширование и WebSocket состояния)
- WebSockets (real-time коммуникация)
- Docker (контейнеризация)

### Frontend
- React/Vue.js (клиентская часть)
- WebSocket API
- Современный адаптивный дизайн

## Требования

- Docker и Docker Compose
- Python 3.8 или выше
- PostgreSQL 13+
- Redis 6+

## Установка и запуск с Docker

1. Клонируйте репозиторий:

```bash
git clone https://github.com/ваш-username/лото-игра.git
cd лото-игра
```

2. Создайте файл .env с необходимыми переменными окружения:

```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=bingo_db
REDIS_HOST=redis
REDIS_PORT=6379
```

3. Запустите приложение с помощью Docker Compose:

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

### REST API
- POST /api/auth/register - Регистрация нового пользователя
- POST /api/auth/login - Вход в систему
- GET /api/games - Список активных игр
- POST /api/games - Создание новой игры
- GET /api/games/{game_id} - Информация об игре
- GET /api/users/me - Информация о текущем пользователе
- GET /api/leaderboard - Таблица лидеров

### WebSocket Endpoints
- /ws/game/{game_id} - WebSocket соединение для игры
- /ws/chat/{game_id} - WebSocket соединение для чата

## Архитектура проекта

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   └── tests/
├── frontend/
│   ├── src/
│   └── public/
├── docker/
└── docker-compose.yml
```

## Разработка

Для локальной разработки:

1. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Запустите миграции:

```bash
alembic upgrade head
```

4. Запустите сервер разработки:

```bash
uvicorn app.main:app --reload
```

## Тестирование

```bash
pytest backend/tests
```

## Лицензия
Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.

Этот README:

1. Дает общее представление о проекте
2. Описывает основные функции
3. Содержит инструкции по установке и запуску
4. Предлагает возможные улучшения
5. Указывает на требования и лицензию

Вы можете адаптировать его под свои нужды, добавив:

- Скриншоты
- Видеодемонстрацию
- Информацию о себе
- Ссылки на другие проекты
- Раздел "Как внести вклад" для open-source проектов
