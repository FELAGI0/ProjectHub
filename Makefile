# Makefile для ProjectHub
.PHONY: up down logs test-unit test-integration test lint format typecheck alembic-check check migrate revision clean help
.DEFAULT_GOAL := help

PYTHON := .venv\Scripts\python.exe

help:  ## Показать все цели
	@$(PYTHON) -c "print('up          Поднять docker compose'); print('down        Остановить docker compose'); print('logs        Показать логи docker compose'); print('test-unit   Только unit + API'); print('test-integration Только integration'); print('test        Запустить все тесты'); print('lint        Проверить код через Ruff'); print('format      Отформатировать код и исправить Ruff'); print('typecheck   Проверить типы через mypy'); print('alembic-check Проверить миграции Alembic'); print('check       Запустить все проверки'); print('migrate     Применить миграции'); print('revision    Создать миграцию: make revision msg=описание'); print('clean       Удалить кэши')"

up:  ## Поднять docker compose
	docker compose up -d

down:  ## Остановить docker compose
	docker compose down

logs:  ## Показать логи docker compose
	docker compose logs -f

test-unit:  ## Только unit + API (без Docker)
	$(PYTHON) -m pytest tests -q -m "not integration"

test-integration:  ## Только integration (нужен Docker)
	$(PYTHON) -m pytest tests -m integration -v

test:  ## Все тесты (unit + integration, нужен Docker)
	$(PYTHON) -m pytest tests -q

lint:  ## Проверить код через Ruff
	$(PYTHON) -m ruff check .

format:  ## Отформатировать код и исправить Ruff
	$(PYTHON) -m ruff format . && $(PYTHON) -m ruff check --fix .

typecheck:  ## Проверить типы через mypy
	$(PYTHON) -m mypy app

alembic-check:  ## Проверить миграции Alembic
	$(PYTHON) -m alembic check

check: lint typecheck test alembic-check  ## Запустить все проверки

migrate:  ## Применить миграции
	$(PYTHON) -m alembic upgrade head

revision:  ## Создать миграцию
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

clean:  ## Удалить кэши
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(path) for path in pathlib.Path('.').rglob('__pycache__') if path.is_dir()]; [shutil.rmtree(path) for path in map(pathlib.Path, ['.pytest_cache', '.mypy_cache', '.ruff_cache']) if path.exists()]"
