# Makefile for PDF Knowledge Graph Extraction System

.PHONY: help install install-dev run test lint format clean build docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install project dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  run         - Run the FastAPI server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black"
	@echo "  clean       - Clean cache and build files"
	@echo "  build       - Build project package"
	@echo "  docs        - Build documentation"

# Installation
install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"
	python -m spacy download en_core_web_sm
	python -m spacy download en_core_web_lg

# Run server
run:
	cd backend && python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Testing
test:
	python -m pytest tests/ -v --cov=backend

# Code quality
lint:
	flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 backend/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black backend/
	black tests/

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Build
build:
	python setup.py sdist bdist_wheel

# Documentation
docs:
	cd docs && make html

# Docker commands
docker-build:
	docker build -t pdf-kg-extractor .

docker-run:
	docker run -p 8000:8000 pdf-kg-extractor

# Development shortcuts
dev: install-dev
	@echo "Development environment ready!"

start: run

check: lint test
	@echo "Code quality checks passed!"
