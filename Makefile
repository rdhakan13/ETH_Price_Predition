YML_FILE = environment.yml
ENV_NAME = STD_DS_LIB

.PHONY: create-env list-packages update-env remove-env

.ONESHELL:

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
