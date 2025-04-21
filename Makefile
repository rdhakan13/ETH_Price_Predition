SCRIPT_NAME = pipeline/2_processed_data.py
LOG_DIR = logs
TMP_DIR = temp
PYTEST_CACHE = .pytest_cache
SRC = ./src/
SCRIPTS = ./scripts/
YML_FILE = environment.yml
ENV_NAME = STD_DS_LIB
EC2_SETUP_SCRIPT = ./scripts/setup.sh
VENV = .venv
POETRY = $(VENV)/bin/poetry

export LOG_LEVEL = INFO

.ONESHELL:
.PHONY: activate init install export-env create-env list-packages update-env remove-env

activate:
	@echo Activating virtual environment...
ifeq ($(OS),Windows_NT)
	.\.venv\Scripts\activate
else
	. .venv/bin/activate
endif

init:
ifeq ($(OS),Windows_NT)
	@if not exist .venv (python -m venv .venv)
	python -m pip install -r requirements.txt
else
	@test -d .venv || python3 -m venv .venv
	python3 -m pip install -r requirements.txt
endif
	poetry config virtualenvs.create false

install: activate
	poetry install --no-root --only main 

exp-env:
	@echo Exporting conda environment...
	conda env export --no-builds > $(YML_FILE)

create-env:
	@echo Creating conda environment
	conda env create -f $(YML_FILE)

list-packages:
	@echo Listing conda packages...
	pip list

update-env:
	@echo Updating conda environment...
	conda env update -f $(YML_FILE) --prune

remove-env:
	@echo Removing conda environment...
	conda env remove -n $(ENV_NAME) 

onetime-setup-ec2:
	@echo Setting up EC2 instance...
	bash $(EC2_SETUP_SCRIPT)
	@echo Done!

clean: activate
	@echo Cleaning up...
	ruff clean
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist $(LOG_DIR) rmdir /s /q $(LOG_DIR)
	if exist $(TMP_DIR) rmdir /s /q $(TMP_DIR)
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist htmlcov rmdir /s /q htmlcov
	if exist .coverage del /q .coverage
	@echo Done!

lint-check: activate
ifeq ($(OS),Windows_NT)
	@echo Lint checking src...
	ruff check $(SRC) --ignore F401
	@echo Lint checking scripts...
	ruff check $(SCRIPTS) --ignore F401
else
	@echo Lint checking src...
	.venv/bin/ruff check $(SRC) --ignore F401
	@echo Lint checking scripts...
	.venv/bin/ruff check $(SCRIPTS) --ignore F401
endif

lint-format: activate
	@echo Lint formatting src...
	ruff format $(SRC)
	@echo Lint formatting scripts...
	ruff format $(SCRIPTS)
	@echo Done!

lint-fix: activate
	@echo Lint formatting and fixing s...
	ruff check $(SRC) --fix --ignore F401
	@echo Lint formatting and fixing scripts...
	ruff check $(SCRIPTS) --fix --ignore F401
	@echo Done!

type-check: activate
	@echo Type checking...
ifeq ($(OS),Windows_NT)
	mypy --config-file pyproject.toml $(SRC)
else
	.venv/bin/mypy $(SRC)
endif

run-script:
	@echo Running script...
	python $(SCRIPTS)$(SCRIPT_NAME)
	@echo Done!

print-env-variables:
	@echo $(LOG_LEVEL)

unit-tests: activate
	@echo Running unit tests...
ifeq ($(OS),Windows_NT)
	pytest --cov=. --cov-report=term-missing --cov-fail-under=80 tests/
else
	.venv/bin/pytest --cov=. --cov-report=term-missing --cov-fail-under=80 tests/
endif

