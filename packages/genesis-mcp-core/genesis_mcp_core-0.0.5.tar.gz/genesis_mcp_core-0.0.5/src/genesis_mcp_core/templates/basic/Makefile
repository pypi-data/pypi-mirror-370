# {{ project_name | title }} - Development Makefile
# Generated from Genesis MCP Core basic template

.PHONY: help install dev start ping health tools client clean test lint format

# Default target
help: ## Show this help message
	@echo "🚀 {{ project_name | title }} - Development Commands"
	@echo "=================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	poetry install

dev: ## Run development server
	@echo "🚀 Starting {{ project_name | title }} development server..."
	poetry run python main.py

start: ## Start production server
	@echo "🌟 Starting {{ project_name | title }} production server..."
	poetry run uvicorn main:app --host 0.0.0.0 --port 8002

ping: ## Quick health check
	@echo "🏥 Checking server health..."
	@curl -s http://localhost:8002/health | python -m json.tool || echo "❌ Server not responding"

health: ## Detailed health check
	@echo "🏥 Detailed health check..."
	@curl -s http://localhost:8002/health | python -m json.tool

tools: ## List available tools
	@echo "🛠️ Available MCP tools..."
	@curl -s http://localhost:8002/tools | python -m json.tool

client: ## Run MCP client test (if available)
	@if [ -f "test_mcp_client.py" ]; then \
		echo "🧪 Running MCP client tests..."; \
		poetry run python test_mcp_client.py; \
	else \
		echo "⚠️ test_mcp_client.py not found. Create one to test your MCP server."; \
	fi

test: ## Run tests
	@echo "🧪 Running tests..."
	@if [ -d "tests" ]; then \
		poetry run pytest tests/ -v; \
	else \
		echo "⚠️ No tests directory found. Create tests/ directory with test files."; \
	fi

lint: ## Run linting
	@echo "🔍 Running linter..."
	poetry run black --check .
	poetry run isort --check-only .

format: ## Format code
	@echo "✨ Formatting code..."
	poetry run black .
	poetry run isort .

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Development shortcuts
d: dev ## Shortcut for dev
s: start ## Shortcut for start  
p: ping ## Shortcut for ping
h: health ## Shortcut for health
t: tools ## Shortcut for tools
c: client ## Shortcut for client
