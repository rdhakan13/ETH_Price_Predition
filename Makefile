SCRIPT_NAME = pipeline/2_processed_data.py
LOG_DIR = ./logs
TMP_DIR = ./tmp
SRC = ./src/
SCRIPTS = ./scripts/
YML_FILE = environment.yml
ENV_NAME = STD_DS_LIB
EC2_SETUP_SCRIPT = ./scripts/setup.sh

export LOG_LEVEL = INFO

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
	rmdir /s /q $(TMP_DIR)
	@echo Done!

lint: 
	@echo Lint formatting src...
	ruff format $(SRC)
	@echo Lint formatting scripts...
	ruff check $(SCRIPTS)
	ruff format $(SCRIPTS)
	@echo Done!

lint-fix: 
	@echo Lint formatting and fixing s...
	ruff check $(SRC) --fix --ignore F401
	ruff format $(SRC)
	@echo Lint formatting and fixing scripts...
	ruff check $(SCRIPTS) --fix --ignore F401
	ruff format $(SCRIPTS)
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