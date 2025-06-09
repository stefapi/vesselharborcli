# Makefile for VesselHarbor CLI development

PYTHON ?= python3

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help = match.groups()
        print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help install dev clean lint format test test-cov mypy run build debug all-checks

help: ## ℹ️ Display help information about available commands
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


install: ## 📦 Install the package and dependencies
	pip install -e .


dev: ## 🛠️ Install development dependencies
	pip install -e ".[dev]"


clean: ## 🧹 Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete


lint: ## 🔍 Run linting checks
	black --check vesselharborcli tests
	isort --check vesselharborcli tests


format: ## 🎨 Format code
	black vesselharborcli tests
	isort vesselharborcli tests


test: ## 🧪 Run tests
	pytest


test-cov: ## 📊 Run tests with coverage
	pytest --cov=vesselharborcli --cov-report=term --cov-report=html


mypy: ## 🧮 Run type checking
	mypy vesselharborcli


run: ## 🚀 Run the CLI application
	python -m vesselharborcli.cli


build: ## 🏗️ Build the package
	pip install build
	python -m build


debug: ## 🐛 Run the CLI application in debug mode
	PYTHONPATH=. python -m pdb -c continue main.py


all-checks: lint mypy test ## ✅ Run all checks
