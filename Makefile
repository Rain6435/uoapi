# Development commands
.PHONY: help
help:		## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Testing commands
.PHONY: t test test-unit test-integration test-cli test-coverage
t: test		## Alias for test
test:		## Run all tests with coverage
	~/.local/bin/pytest

test-unit:	## Run only unit tests
	~/.local/bin/pytest -m "unit"

test-integration:	## Run only integration tests
	~/.local/bin/pytest -m "integration"

test-cli:	## Run only CLI tests
	~/.local/bin/pytest -m "cli"

test-coverage:	## Run tests and open coverage report
	~/.local/bin/pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-fast:	## Run tests without coverage (faster)
	~/.local/bin/pytest --no-cov

# Code quality commands
.PHONY: c check check-all lint format format-check
c: check	## Alias for check
check:		## Run type checking with mypy
	mypy src/

check-all:	## Run all code quality checks
	@echo "Running type checking..."
	mypy src/
	@echo "Running linting..."
	flake8 src/ tests/
	@echo "Running format check..."
	black --check src/ tests/
	@echo "Running security scan..."
	bandit -r src/ -ll

l: lint		## Alias for lint
lint:		## Run linting with flake8
	flake8 src/ tests/

format:		## Format code with black
	black src/ tests/

format-check:	## Check code formatting
	black --check --diff src/ tests/

# Security and dependencies
.PHONY: security deps-check deps-update
security:	## Run security scan with bandit
	bandit -r src/ -ll

deps-check:	## Check for outdated dependencies
	pip list --outdated

deps-update:	## Update dependencies (be careful!)
	pip install --upgrade pip
	pip install --upgrade -e .[tests]

# Build and release commands
.PHONY: build clean install install-dev
build:		## Build the package
	python -m build

clean:		## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:	## Install the package
	pip install -e .

install-dev:	## Install with development dependencies
	pip install -e .[tests]
	pip install black flake8 mypy bandit pytest-cov

# Git and release commands
.PHONY: version-patch version-minor version-major release
version-patch:	## Bump patch version (1.2.0 -> 1.2.1)
	@echo "Current version: $$(cat src/uoapi/__version__.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')"
	@read -p "Enter new patch version (x.y.Z): " version; \
	echo "__version__ = \"$$version\"" > src/uoapi/__version__.py
	@echo "Updated to version: $$(cat src/uoapi/__version__.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')"

version-minor:	## Bump minor version (1.2.0 -> 1.3.0)
	@echo "Current version: $$(cat src/uoapi/__version__.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')"
	@read -p "Enter new minor version (x.Y.0): " version; \
	echo "__version__ = \"$$version\"" > src/uoapi/__version__.py
	@echo "Updated to version: $$(cat src/uoapi/__version__.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')"

version-major:	## Bump major version (1.2.0 -> 2.0.0)
	@echo "Current version: $$(cat src/uoapi/__version__.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')"
	@read -p "Enter new major version (X.0.0): " version; \
	echo "__version__ = \"$$version\"" > src/uoapi/__version__.py
	@echo "Updated to version: $$(cat src/uoapi/__version__.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')"

release:	## Build and prepare for release
	@echo "Running all checks before release..."
	$(MAKE) check-all
	$(MAKE) test
	$(MAKE) clean
	$(MAKE) build
	@echo "Release ready! Run 'twine upload dist/*' to publish."

# CI/CD simulation
.PHONY: ci ci-local
ci:		## Run full CI pipeline locally
	@echo "=== Running CI Pipeline Locally ==="
	$(MAKE) clean
	$(MAKE) install-dev
	$(MAKE) check-all
	$(MAKE) test
	$(MAKE) build
	@echo "=== CI Pipeline Completed Successfully ==="

ci-local:	## Run local CI without installing dependencies
	@echo "=== Running Local CI Checks ==="
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) check
	$(MAKE) test-fast
	@echo "=== Local CI Completed ==="
