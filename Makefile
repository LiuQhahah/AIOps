.PHONY: help setup install test lint format clean
.PHONY: setup-local test-e2e inject-issue clean-local run-agent-local logs

help:
	@echo "Multi-Cloud OpsAgent - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install dependencies"
	@echo "  make format         - Format code with black"
	@echo "  make lint           - Lint code with ruff"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo ""
	@echo "Local E2E Environment:"
	@echo "  make setup-local    - Setup Kind cluster and local environment"
	@echo "  make run-agent-local - Run agent locally"
	@echo "  make inject-issue   - Inject test issues into cluster"
	@echo "  make test-e2e       - Run E2E tests"
	@echo "  make logs           - Tail agent logs"
	@echo "  make clean-local    - Cleanup local environment"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run in Docker"

# Development
install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

format:
	black src/ tests/
	ruff check --fix src/ tests/

lint:
	ruff check src/ tests/
	mypy src/

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v -m unit

# Local E2E Environment
setup-local:
	@echo "🚀 Setting up local E2E environment..."
	@bash scripts/setup-local-env.sh

run-agent-local:
	@echo "🤖 Running OpsAgent in local mode..."
	python -m src.main --config config/config.local.yaml

inject-issue:
	@echo "💉 Injecting test issues..."
	@kubectl scale deployment test-app -n test-app --replicas=20
	@echo "✅ Scaled test-app to 20 replicas (should trigger detection)"

test-e2e:
	@echo "🧪 Running E2E tests..."
	@bash scripts/run-e2e-tests.sh

logs:
	@kubectl logs -n ops-agent -l app=ops-agent -f --tail=50

clean-local:
	@echo "🧹 Cleaning local environment..."
	@bash scripts/teardown-local-env.sh

# Docker
docker-build:
	docker build -t ops-agent:latest .

docker-run:
	docker run --rm -v ~/.kube:/root/.kube -v ~/.aws:/root/.aws ops-agent:latest

# Utilities
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/ *.egg-info
