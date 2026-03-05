# ==============================================================================
# BeatsForRunning — Project Makefile
# ==============================================================================
# Usage:
#   make          → show this help
#   make install  → install package dependencies
#   make test     → run the full test suite
#   make lint     → run linter (ruff)
#   make format   → format code (ruff)
#   make check    → format, lint, typecheck, test
# ==============================================================================

PYTHON    ?= python
PIP       ?= pip
VENV      := .venv
TEST_DIR  := tests
SRC_DIR   := .

ifeq ($(OS),Windows_NT)
	VENV_BIN := $(VENV)/Scripts
else
	VENV_BIN := $(VENV)/bin
endif

.DEFAULT_GOAL := help

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
.PHONY: help
help:          ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ------------------------------------------------------------------------------
# Environment / Installation
# ------------------------------------------------------------------------------
.PHONY: venv
venv:          ## Create a local virtual environment
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Activate with:"
	@echo "  source $(VENV_BIN)/activate   (Linux/macOS)"
	@echo "  $(VENV_BIN)\\activate          (Windows)"

.PHONY: install
install:       ## Install package dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov ruff mypy pytest-bdd

# ------------------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------------------
.PHONY: test
test:          ## Run the full test suite
	$(PYTHON) -m pytest $(TEST_DIR) -v

.PHONY: test-cov
test-cov:      ## Run tests with coverage report
	$(PYTHON) -m pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

# ------------------------------------------------------------------------------
# Code Quality
# ------------------------------------------------------------------------------
.PHONY: lint
lint:          ## Lint source and tests with ruff
	$(PYTHON) -m ruff check $(SRC_DIR)

.PHONY: format
format:        ## Auto-format source and tests with ruff
	$(PYTHON) -m ruff format $(SRC_DIR)

.PHONY: typecheck
typecheck:     ## Run static type checking with mypy
	$(PYTHON) -m mypy $(SRC_DIR) --exclude $(VENV)

.PHONY: check
check: lint format typecheck test  ## Run all quality checks (lint + format + types + tests)

# ------------------------------------------------------------------------------
# Run
# ------------------------------------------------------------------------------
.PHONY: run
run:           ## Run the web server
	$(PYTHON) client.py

# ------------------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------------------
.PHONY: clean
clean:         ## Remove build artifacts, caches, and compiled files
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage