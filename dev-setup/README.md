# Project Setup with Makefile

This project uses a `Makefile` to automate tasks related to managing a Conda environment. The `Makefile` allows you to easily create, update, and remove a Conda environment for the project.

## Prerequisites

Before using the `Makefile`, make sure you have the following installed on your system:

1. **Conda**: The `Makefile` relies on Conda to manage virtual environments. You can download and install Conda from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
   
2. **Make**: You need the `make` utility to execute the commands in the `Makefile`. Most Linux/macOS systems come with `make` preinstalled. On Windows, you can install `make` by downloading the wizard from [GCC for Windows](https://sourceforge.net/projects/gnuwin32/files/make/3.81/make-3.81.exe/download?use_mirror=altushost-swe&download=).

3. **Python**: Ensure that you have Python installed (though Conda will handle this when creating the environment).

## Usage Instructions

The `Makefile` includes several targets for managing the Conda environment. Use `make` followed by the target name to perform the desired action.

1. Open `cmd` in VS code and move into dev-setup folder:
    ```
    cd dev-setup
    ```

2. Execute one of the below make commands:

### Available Targets:

**Create a new Conda environment**:
   This target creates a new Conda environment from the `environment.yml` file and installs the specified version of Python:
   ```
   make create-env
   ```

**List packages in Conda environment**:
   This target list packages in the Conda environment from the `environment.yml` file:
   ```
   make list-packages
   ```

**Update an existing Conda environment**:
   This target updates the Conda environment based on changes in the `environment.yml` file. Update the dependencies as needed with python packages and respective versions:
   ```
   make update-env
   ```

**Remove the Conda environment**:
    This target removes the Conda environment entirely:
    ```
    make remove-env
    ```

3. Activate the environment:
    ```
    conda activate STD_DS_LIB
    ```

To deactivate the environment:
```
conda deactivate
```