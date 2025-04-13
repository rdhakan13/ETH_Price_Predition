SCRIPT_NAME = pipeline/2_processed_data.py
LOG_DIR = logs
TMP_DIR = tmp
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
	conda env export > $(YML_FILE)

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

clean:
	@echo Cleaning up...
	ruff clean
	rmdir /s /q .mypy_cache
	rmdir /s /q $(LOG_DIR)
	rmdir /s /q $(TMP_DIR)
	rmdir /s /q .pytest_cache
	rmdir /s /q htmlcov
	@echo Done!

lint-format: 
	@echo Lint formatting src...
	ruff format $(SRC)
	@echo Lint formatting scripts...
	ruff check $(SCRIPTS)
	ruff format $(SCRIPTS)
	@echo Done!

lint-fix: 
	@echo Lint formatting and fixing s...
	ruff check $(SRC) --fix --ignore F401
	@echo Lint formatting and fixing scripts...
	ruff check $(SCRIPTS) --fix --ignore F401
	@echo Done!

type-check:
	@echo Type checking...
	mypy --no-cache-dir $(SRC)
	@echo Done!

run-script:
	@echo Running script...
	python $(SCRIPTS)$(SCRIPT_NAME)
	@echo Done!

print-env-variables:
	@echo $(LOG_LEVEL)

unit-tests: activate
	@echo Running unit tests...
	pytest --cov=. --cov-report=term --cov-report=html tests/
	@echo Done!