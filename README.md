# :rocket: Ethereum price prediction using hybrid deep learning algorithms

## :page_facing_up: Overview

## :floppy_disk: Dataset

## :open_file_folder: Project Structure

## :gear: How to Run

This project uses a `Makefile` to automate tasks related to managing a Python environment, code clean-up and running scripts.

### Prerequisites

Before using the `Makefile`, make sure you have the following installed on your system:

1. **Python**: Ensure that you have Python 3.11.7 installed.
   
2. **Make**: You need the `make` utility to execute the commands in the `Makefile`. Most Linux/macOS systems come with `make` preinstalled. On Windows, you can install `make` by downloading the wizard from [GCC for Windows](https://sourceforge.net/projects/gnuwin32/files/make/3.81/make-3.81.exe/download?use_mirror=altushost-swe&download=). Install `make` by running the wizard and copying the path of executable into PATH variable under 'Edit environmental variables for your account' in control panel. You can find the path of the executable by running `where make` in the terminal.

### Usage Instructions

The `Makefile` includes several targets:

#### Setting up Python Environment:

1. **Create a .venv**:
    This target creates a new .venv environment using the `requirements.txt` file:
    ```
    make init
    ```
2. **Install Python libraries using Poetry**:
    This target installs dependencies listed in pyproject.toml:
    ```
    make install
    ```
3. **Activate .venv**

#### Local testing & Linting:

- **Linting**:

    To check linting:
    ```
    make lint-check
    ```
    To lint format
    ```
    make lint-format
    ```
    To check linting and fix issues:
    ```
    make lint-fix
    ```
- **Type check**

    To conduct a type check across `src`:
    ```
    make type-check
    ```
- **Unit Tests**

    To conduct local unit tests:
    ```
    make unit-tests
    ```
- **Clean folder directory**

    To remove cache folders:
    ```
    make clean
    ```
## :books: References