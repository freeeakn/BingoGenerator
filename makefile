all:
	docker compose up --build

down:
	docker compose down

migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

