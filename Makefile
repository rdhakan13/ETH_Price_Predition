SCRIPT_NAME = main.py
SRC = ./src/
YML_FILE = environment.yml
ENV_NAME = STD_DS_LIB
EC2_SETUP_SCRIPT = ./scripts/setup.sh

.ONESHELL:
.PHONY:

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

list-packages:
	@echo Listing python packages...
	pip list

onetime-setup-ec2:
	@echo Setting up EC2 instance...
	bash $(EC2_SETUP_SCRIPT)
	@echo Done!

clean: activate
	@echo Cleaning up...
	ruff clean
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist logs rmdir /s /q logs
	if exist temp rmdir /s /q temp
	if exist tmp rmdir /s /q tmp
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist htmlcov rmdir /s /q htmlcov
	if exist .coverage del /q .coverage
	@echo Done!

lint-check: activate
ifeq ($(OS),Windows_NT)
	@echo Lint checking src...
	ruff check $(SRC) --ignore F401
else
	@echo Lint checking src...
	.venv/bin/ruff check $(SRC) --ignore F401
endif

lint-format: activate
	@echo Lint formatting src...
	ruff format $(SRC)
	@echo Done!

lint-fix: activate
	@echo Lint formatting and fixing s...
	ruff check $(SRC) --fix --ignore F401
	@echo Done!

type-check: activate
	@echo Type checking...
ifeq ($(OS),Windows_NT)
	mypy $(SRC)
else
	.venv/bin/mypy $(SRC)
endif

run-script:
	@echo Running script...
	python $(SCRIPT_NAME)
	@echo Done!

run:
ifeq ($(OS),Windows_NT)
	@python -c "import os, sys; \
	from pathlib import Path; \
	matches = list(Path('.').rglob('$(FILE)')); \
	f = os.path.abspath(matches[0]) if matches else sys.exit(f'File \"$(FILE)\" not found'); \
	print('Running', f); \
	os.system(f'python \"{f}\"')"
else
	@filename=$(FILE); \
	fullpath=$$(readlink -f $$filename); \
	echo "Running $$fullpath"; \
	python3 $$fullpath
endif

unit-tests: activate
	@echo Running unit tests...
ifeq ($(OS),Windows_NT)
	pytest --cov=. --cov-report=term-missing --cov-fail-under=70 tests/
else
	.venv/bin/pytest --cov=. --cov-report=term-missing --cov-fail-under=70 tests/
endif

lines-of-code-report:
	@echo Counting lines of code...
	cloc --include-lang=Python --by-file --report-file=cloc_report.txt $(SRC)

start-mlflow:activate
	@echo Starting MLflow UI...
	mlflow ui --backend-store-uri sqlite:///mlruns/mlruns.db --host localhost --port 5000

start-jupyter:activate
	@echo Starting Jupyter Notebook...
	jupyter notebook