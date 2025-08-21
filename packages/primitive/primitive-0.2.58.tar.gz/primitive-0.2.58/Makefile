# Makefile with phony targets

.PHONY: setup lint format setup-hooks services
# OS := $(shell uname)

.ONESHELL:
SHELL := /opt/homebrew/bin/fish
# .SHELLFLAGS += -e
setup : ## Setup Environment
	@make setup-git-hooks
	uv sync

setup-ci: ## Setup the environment for CI
	uv sync

test: ## test
	@ENVIRONMENT=test python run pytest

lint: ## Lint Python Files
	uv run ruff check
	# pyright

format: ## Format Python Files
	uv run ruff format
	uv run ruff check --fix

install: ## Install dependencies
	uv sync

setup-git-hooks: ## Setup Git Hook
	@echo "Setting up Git hooks..."
	cp ./.git-hooks/pre-commit ./.git/hooks/pre-commit
	chmod +x ./.git/hooks/pre-commit

build: ## Build the project
	@hatch build

help: ## show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)