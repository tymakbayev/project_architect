# Makefile for Project Architect

.PHONY: setup install dev clean lint format type-check test test-cov test-integration docs build docker docker-build docker-run help all

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := pytest
PYTEST_ARGS := -v
PYTEST_COV_ARGS := --cov=src --cov-report=term --cov-report=html
PYTEST_INTEGRATION_ARGS := -v tests/integration
VENV_NAME := venv
VENV_BIN := $(VENV_NAME)/bin
VENV_ACTIVATE := . $(VENV_BIN)/activate
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
BUILD_DIR := build
DIST_DIR := dist
DOCKER_IMAGE_NAME := project-architect
DOCKER_TAG := latest
DOCKER_FILE := Dockerfile

# Default target
all: setup lint type-check test

help:
	@echo "Project Architect Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make setup              Install development dependencies and set up environment"
	@echo "  make install            Install the package"
	@echo "  make dev                Install the package in development mode"
	@echo "  make clean              Remove build artifacts and cache files"
	@echo "  make lint               Run linting tools (flake8, black, isort)"
	@echo "  make format             Format code with black and isort"
	@echo "  make type-check         Run mypy for type checking"
	@echo "  make test               Run unit tests"
	@echo "  make test-cov           Run tests with coverage report"
	@echo "  make test-integration   Run integration tests"
	@echo "  make docs               Build documentation"
	@echo "  make build              Build the package"
	@echo "  make docker-build       Build Docker image"
	@echo "  make docker-run         Run the application in Docker"
	@echo "  make all                Run setup, lint, type-check, and test"
	@echo "  make help               Show this help message"

# Environment setup
setup: clean
	$(PYTHON) -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev,docs]"
	pre-commit install

install:
	$(PIP) install .

dev:
	$(PIP) install -e ".[dev]"

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) .eggs *.egg-info
	rm -rf .coverage htmlcov .pytest_cache .mypy_cache
	rm -rf $(DOCS_DIR)/_build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Code quality
lint: lint-flake8 lint-black lint-isort

lint-flake8:
	flake8 $(SRC_DIR) $(TEST_DIR)

lint-black:
	black --check $(SRC_DIR) $(TEST_DIR)

lint-isort:
	isort --check-only --profile black $(SRC_DIR) $(TEST_DIR)

format:
	isort --profile black $(SRC_DIR) $(TEST_DIR)
	black $(SRC_DIR) $(TEST_DIR)

type-check:
	mypy $(SRC_DIR)

# Testing
test:
	$(PYTEST) $(PYTEST_ARGS) $(TEST_DIR)/unit

test-cov:
	$(PYTEST) $(PYTEST_ARGS) $(PYTEST_COV_ARGS) $(TEST_DIR)/unit

test-integration:
	$(PYTEST) $(PYTEST_INTEGRATION_ARGS)

test-all: test-cov test-integration

# Documentation
docs:
	cd $(DOCS_DIR) && make html

docs-serve: docs
	cd $(DOCS_DIR)/_build/html && python -m http.server 8000

# Packaging
build: clean
	$(PYTHON) -m build

# Docker
docker-build:
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) -f $(DOCKER_FILE) .

docker-run:
	docker run -it --rm -p 8000:8000 --env-file .env $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)

docker-compose-up:
	docker-compose up

docker-compose-down:
	docker-compose down

# Release workflow
release-check: lint type-check test-all build
	twine check dist/*

release-test: release-check
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release: release-check
	twine upload dist/*

# Development utilities
run-dev:
	uvicorn src.interfaces.api:app --reload --host 0.0.0.0 --port 8000

run-cli:
	python -m src.interfaces.cli

# Git helpers
git-clean:
	git clean -xdf -e .env -e venv

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Security checks
security-check:
	bandit -r $(SRC_DIR)
	safety check

# Dependencies
requirements:
	pip-compile --output-file=requirements.txt pyproject.toml

requirements-dev:
	pip-compile --extra=dev --output-file=requirements-dev.txt pyproject.toml

requirements-docs:
	pip-compile --extra=docs --output-file=requirements-docs.txt pyproject.toml

requirements-all:
	pip-compile --extra=dev,docs --output-file=requirements-all.txt pyproject.toml

# Default target
.DEFAULT_GOAL := help