# Use uv if you have it; fall back to pip/python if not.
UV ?= $(shell command -v uv 2>/dev/null)

ifeq ($(UV),)
PY ?= python
PIP ?= pip
RUN ?= $(PY) -m
DEV_INSTALL = $(PIP) install -e ".[dev]"
EDITABLE_INSTALL = $(PIP) install -e .
BUILD = $(PY) -m build
PUBLISH = $(PY) -m twine upload dist/*
TEST_INSTALL_PKG = $(PIP) install always-decimal --no-cache-dir
else
PY ?= uv run python
PIP ?= uv pip
RUN ?= uv run
DEV_INSTALL = uv pip install -e ".[dev]"
EDITABLE_INSTALL = uv pip install -e .
BUILD = uv build
# uv publish supports token via UV_PUBLISH_TOKEN; twine uses TWINE_PASSWORD.
# Keep both options; default to uv if present.
PUBLISH = uv publish
TEST_INSTALL_PKG = uv add always-decimal
endif

.PHONY: help
help:
	@echo "Targets:"
	@echo "  venv            Create a local venv (.venv) using uv (if available)"
	@echo "  dev             Editable install with dev deps"
	@echo "  install         Editable install (runtime only)"
	@echo "  fmt             Format with ruff"
	@echo "  lint            Lint with ruff"
	@echo "  type            Type-check with mypy"
	@echo "  test            Run tests"
	@echo "  build           Build sdist/wheel"
	@echo "  publish         Publish to PyPI (requires token)"
	@echo "  publish-test    Publish to TestPyPI"
	@echo "  clean           Remove build artifacts"
	@echo "  verify-install  Create fresh venv and install package from PyPI"

.PHONY: venv
venv:
	@if [ -n "$(UV)" ]; then uv venv; else python -m venv .venv; fi
	@echo "Activate with: source .venv/bin/activate"

.PHONY: dev
dev:
	$(DEV_INSTALL)

.PHONY: install
install:
	$(EDITABLE_INSTALL)

.PHONY: fmt
fmt:
	$(RUN) ruff format src tests

.PHONY: lint
lint:
	$(RUN) ruff check src tests

.PHONY: type
type:
	$(RUN) mypy src

.PHONY: test
test:
	$(RUN) pytest

.PHONY: build
build:
	rm -rf dist build *.egg-info
	$(BUILD)

.PHONY: publish
publish: build
	@echo "Publishing to PyPI..."
	@if [ -n "$(UV)" ]; then \
		UV_PUBLISH_TOKEN=$$PYPI_TOKEN $(PUBLISH); \
	else \
		TWINE_USERNAME=__token__ TWINE_PASSWORD=$$PYPI_TOKEN $(PUBLISH); \
	fi

.PHONY: publish-test
publish-test: build
	@echo "Publishing to TestPyPI..."
	@if [ -n "$(UV)" ]; then \
		UV_PUBLISH_TOKEN=$$TEST_PYPI_TOKEN $(PUBLISH) --repository testpypi; \
	else \
		TWINE_USERNAME=__token__ TWINE_PASSWORD=$$TEST_PYPI_TOKEN $(RUN) twine upload --repository-url https://test.pypi.org/legacy/ dist/*; \
	fi

.PHONY: clean
clean:
	rm -rf dist build .mypy_cache .pytest_cache *.egg-info

.PHONY: verify-install
verify-install:
	@if [ -n "$(UV)" ]; then \
		rm -rf .tox-verify && uv venv .tox-verify && . .tox-verify/bin/activate && uv pip install --upgrade pip && $(TEST_INSTALL_PKG) && python -c "import always_decimal, sys; print(always_decimal.ensure_decimal(0.1, scale=2))"; \
	else \
		python -m venv .tox-verify && . .tox-verify/bin/activate && pip install --upgrade pip && $(TEST_INSTALL_PKG) && python -c "import always_decimal, sys; print(always_decimal.ensure_decimal(0.1, scale=2))"; \
	fi
