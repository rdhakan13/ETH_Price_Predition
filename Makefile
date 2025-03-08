LOG_DIR = ./logs
TEMP_DIR = ./temp
LINT_SRC = ./src/
LINT_SCRIPTS = ./scripts/
TYPE_CHECK_DIR = ./src/
YML_FILE = environment.yml
ENV_NAME = STD_DS_LIB
EC2_SETUP_SCRIPT = ./scripts/setup.sh

.PHONY: export-env create-env list-packages update-env remove-env

.ONESHELL:

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
	rmdir /s /q $(TEMP_DIR)
	@echo Done!

lint: 
	@echo Linting and fixing...
	ruff check $(LINT_SRC)
	ruff format $(LINT_SRC)
	ruff check $(LINT_SCRIPTS)
	ruff format $(LINT_SCRIPTS)
	@echo Done!

lint-fix: 
	@echo Linting and fixing...
	ruff check $(LINT_SRC) --fix --ignore F401
	ruff format $(LINT_SRC)
	ruff check $(LINT_SCRIPTS) --fix --ignore F401
	ruff format $(LINT_SCRIPTS)
	@echo Done!

type-check:
	@echo Type checking...
	mypy --no-cache-dir $(TYPE_CHECK_DIR)
	@echo Done!