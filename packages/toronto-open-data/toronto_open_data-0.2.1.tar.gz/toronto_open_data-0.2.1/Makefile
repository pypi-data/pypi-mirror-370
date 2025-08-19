.PHONY: help install install-dev test test-cov lint format clean docs build publish

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=toronto_open_data --cov-report=html --cov-report=term

lint:  ## Run linting checks
	flake8 toronto_open_data/ tests/
	black --check toronto_open_data/ tests/
	mypy toronto_open_data/

format:  ## Format code
	black toronto_open_data/ tests/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:  ## Build documentation
	@echo "📚 Building documentation..."
	@if [ -f docs/conf.py ]; then \
		cd docs && python -m sphinx.cmd.build -b html . _build/html; \
	else \
		echo "⚠️  Sphinx documentation not configured. Skipping docs build."; \
	fi

build:  ## Build package
	python -m build

publish: build
	@echo "🚀 Publishing to PyPI..."
	@echo "📝 Note: This will now be handled by GitHub Actions when you create a release"
	@echo "💡 To publish:"
	@echo "   1. Update version in pyproject.toml"
	@echo "   2. Commit and push changes"
	@echo "   3. Create a new release on GitHub (this triggers the workflow)"
	@echo "   4. The workflow will run tests and publish automatically"
	@echo ""
	@echo "🔧 Manual publish (if needed):"
	@echo "   twine upload dist/*"

pre-commit:  ## Install pre-commit hooks
	pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	pre-commit run --all-files

security:  ## Run security checks
	bandit -r toronto_open_data/ -f json -o bandit-report.json
	safety check

check-all:  ## Run all quality checks
	make lint
	make test-cov
	make security
	make docs
