# nonconform Makefile
.DEFAULT_GOAL := help

# Variables
PYTHON := uv run python
UV := uv
DOCS_DIR := docs
DOCS_SOURCE := $(DOCS_DIR)/source
DOCS_BUILD := $(DOCS_DIR)/build
PACKAGE := nonconform
TESTS_DIR := tests

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Declare all phony targets
.PHONY: help install install-dev install-docs install-all install-editable \
        format lint check pre-commit pre-commit-install \
        test test-unit test-functional test-verbose test-specific \
        docs docs-clean docs-serve docs-check docs-autobuild \
        lock sync upgrade show-deps check-outdated \
        build publish-test publish \
        clean clean-all \
        ci-test ci-lint ci-docs ci-all \
        shell watch-tests version info

help: ## Show this help message
	@echo "$(BLUE)nonconform development commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ====================
# Setup & Installation
# ====================

install: ## Install production dependencies
	@echo "$(YELLOW)Installing production dependencies...$(NC)"
	$(UV) sync

install-dev: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	$(UV) sync --extra dev

install-docs: ## Install documentation dependencies
	@echo "$(YELLOW)Installing documentation dependencies...$(NC)"
	$(UV) sync --extra docs

install-all: ## Install all dependencies (dev, docs, data, deep, fdr)
	@echo "$(YELLOW)Installing all dependencies...$(NC)"
	$(UV) sync --all-extras

install-editable: ## Install package in editable mode
	@echo "$(YELLOW)Installing package in editable mode...$(NC)"
	$(UV) pip install -e .

# ====================
# Development
# ====================

format: ## Format code with black and fix ruff issues
	@echo "$(YELLOW)Formatting code...$(NC)"
	$(UV) run black .
	$(UV) run ruff check . --fix

lint: ## Check code style with ruff and black
	@echo "$(YELLOW)Checking code style...$(NC)"
	$(UV) run ruff check .
	$(UV) run black --check --diff .

check: lint ## Alias for lint

pre-commit: ## Run all pre-commit hooks
	@echo "$(YELLOW)Running pre-commit hooks...$(NC)"
	$(UV) run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	@echo "$(YELLOW)Installing pre-commit hooks...$(NC)"
	$(UV) run pre-commit install

# ====================
# Testing
# ====================

test: ## Run all tests
	@echo "$(YELLOW)Running all tests...$(NC)"
	$(PYTHON) -m unittest discover $(TESTS_DIR)

test-unit: ## Run unit tests only
	@echo "$(YELLOW)Running unit tests...$(NC)"
	$(PYTHON) -m unittest discover $(TESTS_DIR)/unit

test-functional: ## Run functional tests only
	@echo "$(YELLOW)Running functional tests...$(NC)"
	$(PYTHON) -m unittest discover $(TESTS_DIR)/functional

test-verbose: ## Run all tests with verbose output
	@echo "$(YELLOW)Running all tests (verbose)...$(NC)"
	$(PYTHON) -m unittest discover $(TESTS_DIR) -v

test-specific: ## Run specific test file (use TEST=path/to/test.py)
	@echo "$(YELLOW)Running specific test: $(TEST)$(NC)"
	$(PYTHON) -m unittest $(TEST)

# ====================
# Documentation
# ====================

docs: ## Build HTML documentation
	@echo "$(YELLOW)Building documentation...$(NC)"
	$(UV) run sphinx-build -W --keep-going -b html $(DOCS_SOURCE) $(DOCS_BUILD)/html
	@echo "$(GREEN)Documentation built at $(DOCS_BUILD)/html/index.html$(NC)"

docs-clean: ## Clean documentation build
	@echo "$(YELLOW)Cleaning documentation...$(NC)"
	rm -rf $(DOCS_BUILD)

docs-serve: docs ## Build and serve documentation locally
	@echo "$(GREEN)Serving documentation at http://localhost:8000$(NC)"
	$(PYTHON) -m http.server --directory $(DOCS_BUILD)/html 8000

docs-check: ## Check documentation for broken links
	@echo "$(YELLOW)Checking documentation links...$(NC)"
	$(UV) run sphinx-build -b linkcheck $(DOCS_SOURCE) $(DOCS_BUILD)/linkcheck

docs-autobuild: ## Auto-rebuild docs on changes (requires sphinx-autobuild)
	@echo "$(YELLOW)Starting documentation auto-build...$(NC)"
	$(UV) run sphinx-autobuild $(DOCS_SOURCE) $(DOCS_BUILD)/html

# ====================
# Package Management
# ====================

lock: ## Update uv.lock file
	@echo "$(YELLOW)Updating lock file...$(NC)"
	$(UV) lock

sync: ## Sync environment with lock file
	@echo "$(YELLOW)Syncing environment...$(NC)"
	$(UV) sync --all-extras

upgrade: ## Upgrade all dependencies to latest versions
	@echo "$(YELLOW)Upgrading dependencies to latest versions...$(NC)"
	@echo "$(YELLOW)Step 1: Updating lock file with latest versions...$(NC)"
	$(UV) lock --upgrade
	@echo "$(YELLOW)Step 2: Syncing environment with upgraded dependencies...$(NC)"
	$(UV) sync --all-extras
	@echo "$(GREEN)Dependencies upgraded successfully!$(NC)"

show-deps: ## Show current dependencies
	@echo "$(YELLOW)Current dependencies:$(NC)"
	$(UV) pip list

check-outdated: ## Check for outdated packages
	@echo "$(YELLOW)Checking for outdated packages...$(NC)"
	$(UV) pip list --outdated

# ====================
# Building & Distribution
# ====================

build: clean ## Build distribution packages
	@echo "$(YELLOW)Building distribution packages...$(NC)"
	$(UV) run python -m build

publish-test: build ## Publish to TestPyPI
	@echo "$(YELLOW)Publishing to TestPyPI...$(NC)"
	$(UV) run twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	@echo "$(RED)Publishing to PyPI...$(NC)"
	$(UV) run twine upload dist/*

# ====================
# Cleaning
# ====================

clean: ## Clean build artifacts and cache
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .ruff_cache/ .pytest_cache/ .mypy_cache/
	@echo "$(GREEN)Build artifacts cleaned$(NC)"

clean-all: clean docs-clean ## Clean everything including virtual environment
	@echo "$(YELLOW)Cleaning everything...$(NC)"
	@rm -rf .venv/
	@echo "$(GREEN)Everything cleaned$(NC)"

# ====================
# CI/CD Helpers
# ====================

ci-test: install-dev test ## CI: Install and run tests

ci-lint: install-dev lint ## CI: Install and run linting

ci-docs: install-docs docs ## CI: Install and build documentation

ci-all: install-all lint test docs ## CI: Complete check (install, lint, test, docs)

# ====================
# Development Helpers
# ====================

shell: ## Start Python REPL with package imported
	@echo "$(YELLOW)Starting Python shell...$(NC)"
	@$(PYTHON) -c "import $(PACKAGE); import IPython; IPython.embed()" 2>/dev/null || \
	$(PYTHON) -c "import $(PACKAGE); import code; code.interact(local=locals())"

watch-tests: ## Watch for changes and re-run tests (requires watchdog)
	@echo "$(YELLOW)Watching for changes...$(NC)"
	$(UV) run watchmedo auto-restart --patterns="*.py" --recursive --command="make test"

version: ## Show package version
	@$(PYTHON) -c "import $(PACKAGE); print($(PACKAGE).__version__)"

info: ## Show project information
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Project Information$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "  $(GREEN)Package:$(NC)   $(PACKAGE)"
	@echo "  $(GREEN)Version:$(NC)   $$(make -s version)"
	@echo "  $(GREEN)Python:$(NC)    $$(cat .python-version)"
	@echo "  $(GREEN)Location:$(NC)  $$(pwd)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"